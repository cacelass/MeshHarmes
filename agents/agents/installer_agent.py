"""
agents.agents.installer_agent — Instala agentes externos en `agents/external/`.

Lee el aviso de seguridad en `agents/tools/agent_installer_tool.py` antes de
usar este agente: instalar código de un origen externo significa
ejecutarlo al importarlo. Este agente valida la FORMA (estructura AST) del
código candidato, no su contenido — no sustituye una revisión humana antes
de usar un agente de un origen que no sea de confianza.

Usa `agents/workspace/installer/` para el staging de repos clonados —
nunca clona directamente dentro de `agents/external/`, primero valida en
el workspace y solo copia el archivo concreto si pasa la validación.

También es quien CREA agentes que no existen todavía (`scaffold`), porque el
dueño de `agents/external/` es este agente y no dos. Lo generado es un
esqueleto honesto: acciones que devuelven `success=False` diciendo que están
sin implementar, nunca un éxito falso. Quién detecta que falta un agente es
`bootstrap suggest_agents`; quién lo escribe es esto.
"""

from __future__ import annotations

import shutil

from agents.core.base_agent import AgentResult, BaseAgent
from agents.core.registry import agent_registry, register_agent
from agents.exceptions import MissingDependencyError, ToolExecutionError
from agents.tools.agent_installer_tool import AgentInstallerTool
from agents.tools.agent_scaffold_tool import AgentScaffoldTool, AgentSpec, split_multi

#: Lo que hay que decir del resultado de `scaffold` siempre, en dry-run y en
#: real: un esqueleto no es un agente que funcione.
_AVISO_ESQUELETO = (
    "El agente generado NO hace nada: sus acciones devuelven success=False con lo que "
    "les falta en needs. Impleméntalas antes de prometerle nada al usuario."
)


@register_agent
class InstallerAgent(BaseAgent):
    name = "installer"
    description = (
        "Instala agentes externos (por URL de git o ruta local) en agents/external/, "
        "valida su estructura y confirma que quedan registrados y funcionando."
    )
    capabilities = ["instalar agente", "clonar agente", "agente externo", "añadir agente", "installer"]

    def actions(self) -> dict:
        return {
            "install_from_git": self.install_from_git,
            "install_from_path": self.install_from_path,
            "scaffold": self.scaffold,
            "list_installed": self.list_installed,
            "verify": self.verify,
        }

    # -------------------------------------------------------------------------
    def _stage_and_pick_candidate(self, source_root, *, subpath: str | None):
        """Busca candidatos en `source_root`; si hay más de uno y no se dio
        `subpath`, no adivina — devuelve None y dejar que el llamador falle explícito."""
        if subpath:
            candidate_path = source_root / subpath
            if not candidate_path.exists():
                return None, f"'{subpath}' no existe dentro de lo clonado/copiado."
            candidates = [c for c in AgentInstallerTool.find_agent_candidates(source_root) if c.path == candidate_path]
            if not candidates:
                return None, f"'{subpath}' no contiene ninguna clase con @register_agent."
            return candidates[0], None

        candidates = AgentInstallerTool.find_agent_candidates(source_root)
        if not candidates:
            return None, "No se encontró ninguna clase decorada con @register_agent en el origen."
        if len(candidates) > 1:
            paths = [str(c.path.relative_to(source_root)) for c in candidates]
            return None, f"Se encontraron {len(candidates)} agentes candidatos, especifica 'subpath': {paths}"
        return candidates[0], None

    def _finish_install(self, candidate, *, force: bool) -> AgentResult:
        destination_dir = self.ctx.root / "agents" / "external"
        try:
            installed_path = AgentInstallerTool.install_file(candidate.path, destination_dir, force=force)
        except FileExistsError as exc:
            return AgentResult(False, self.name, "install", str(exc))

        agent_registry.discover(force=True)
        registered = candidate.declared_name in agent_registry.all() if candidate.declared_name else False

        warnings = list(candidate.warnings)
        warnings.append(
            "SEGURIDAD: este código se ejecutó al importarse para verificar el registro. "
            "Revísalo tú mismo si el origen no es de completa confianza."
        )
        if not registered:
            warnings.append(
                "No se pudo confirmar el registro automáticamente (no se detectó 'name = \"...\"' "
                "como literal de clase, o el import falló en silencio) — comprueba con "
                "'python -m agents list' o el agente 'verify'."
            )

        return AgentResult(
            True, self.name, "install",
            f"Agente instalado en '{installed_path}'"
            + (f" y registrado como '{candidate.declared_name}'." if registered else " (registro sin confirmar, ver warnings)."),
            data={"installed_path": str(installed_path), "declared_name": candidate.declared_name, "registered": registered},
            warnings=warnings,
        )

    def install_from_git(self, *, repo_url: str, subpath: str | None = None, force: bool = False) -> AgentResult:
        resolved_url = AgentInstallerTool.normalize_github_shorthand(repo_url)
        workdir = self.ctx.agent_workspace("installer")
        repo_dir_name = resolved_url.rstrip("/").rsplit("/", 1)[-1].removesuffix(".git")
        clone_dir = workdir / repo_dir_name

        if clone_dir.exists():
            shutil.rmtree(clone_dir)
        try:
            AgentInstallerTool.clone_git_repo(resolved_url, clone_dir)
        except MissingDependencyError as exc:
            return AgentResult(False, self.name, "install_from_git", str(exc))
        except ToolExecutionError as exc:
            return AgentResult(False, self.name, "install_from_git", str(exc))

        candidate, error = self._stage_and_pick_candidate(clone_dir, subpath=subpath)
        if candidate is None:
            return AgentResult(False, self.name, "install_from_git", error)

        return self._finish_install(candidate, force=force)

    def install_from_path(self, *, local_path: str, subpath: str | None = None, force: bool = False) -> AgentResult:
        source_root = (self.ctx.root / local_path).resolve()
        if not source_root.exists():
            return AgentResult(False, self.name, "install_from_path", f"No existe '{local_path}'.")

        search_root = source_root if source_root.is_dir() else source_root.parent
        effective_subpath = subpath or (source_root.name if source_root.is_file() else None)

        candidate, error = self._stage_and_pick_candidate(search_root, subpath=effective_subpath)
        if candidate is None:
            return AgentResult(False, self.name, "install_from_path", error)

        return self._finish_install(candidate, force=force)

    # -- scaffold -------------------------------------------------------------

    def _registrar_en_caliente(self, spec: AgentSpec, fuente: str) -> type[BaseAgent]:
        """
        Ejecuta el módulo generado para obtener su clase, ya registrada.

        Dos motivos, ninguno cosmético: `prompts_sync.render_block` necesita el
        agente REGISTRADO para encontrar su contrato inline (si no, el prompt
        saldría sin la sección de límites y `prompts-check` lo marcaría como
        desincronizado); y ejecutarlo comprueba de paso que el módulo importa.
        No es el riesgo de `install_from_*`: este código lo acabamos de escribir
        nosotros a partir de una spec validada, no viene de un tercero.
        """
        espacio: dict = {"__name__": f"agents.external.{spec.module_stem}"}
        exec(compile(fuente, spec.module_path, "exec"), espacio)
        return espacio[spec.class_name]

    @staticmethod
    def _desregistrar(nombre: str) -> None:
        """Deshace `_registrar_en_caliente`. El registro no expone un `unregister`."""
        agent_registry._agents.pop(nombre, None)

    def scaffold(
        self, *, name: str = "", description: str = "", capabilities: str = "",
        actions: str = "", role: str = "", can: str = "", cannot: str = "",
        needs: str = "", owns: str = "", collaborates: str = "", dry_run: bool = True,
    ) -> AgentResult:
        """
        Genera un agente completo: módulo con contrato inline, prompt y test.

        Los campos multivalor van como cadenas separadas por `;`, igual que en
        `harness add --criteria`. Con `dry_run=True` (por defecto) devuelve lo
        que generaría y no escribe ni un byte.

        El prompt no es opcional: un agente registrado sin
        `agents/prompts/<name>_agent.md` deja `prompts_sync` en rojo y tumba el
        CI, así que se genera con el resto o no se genera nada.
        """
        from agents.contracts import all_contracts, validate_contracts
        from agents.prompts_sync import render_block

        spec = AgentSpec(
            name=name.strip(),
            description=" ".join(description.split()),
            capabilities=split_multi(capabilities),
            actions=split_multi(actions),
            role=" ".join(role.split()),
            can=split_multi(can),
            cannot=split_multi(cannot),
            needs=split_multi(needs),
            owns=split_multi(owns),
            collaborates=split_multi(collaborates),
        )

        agent_registry.discover()
        duenos = {r: n for n, c in all_contracts().items() for r in c.owns}
        problemas = AgentScaffoldTool.validar(
            spec, registrados=set(agent_registry.all()), duenos=duenos,
        )
        if problemas:
            return AgentResult(
                False, self.name, "scaffold",
                f"La spec no sirve todavía ({len(problemas)} problema(s)) — no se ha generado nada.",
                data={"problems": problemas}, needs=problemas,
            )

        rutas = {
            spec.module_path: self.ctx.root / spec.module_path,
            spec.prompt_path: self.ctx.root / spec.prompt_path,
            spec.test_path: self.ctx.root / spec.test_path,
        }
        ya_existen = [rel for rel, ruta in rutas.items() if ruta.exists()]
        if ya_existen:
            return AgentResult(
                False, self.name, "scaffold",
                f"No sobrescribo lo que ya hay: {', '.join(ya_existen)}.",
                needs=["Elige otro --name, o borra tú esos ficheros si de verdad quieres regenerarlos."],
            )

        fuente = AgentScaffoldTool.render_module(spec)
        clase = self._registrar_en_caliente(spec, fuente)
        try:
            ficheros = {
                spec.module_path: fuente,
                spec.prompt_path: AgentScaffoldTool.render_prompt(
                    spec, render_block(spec.name, clase(context=self.ctx)),
                ),
                spec.test_path: AgentScaffoldTool.render_test(spec),
            }
            if dry_run:
                return AgentResult(
                    True, self.name, "scaffold",
                    f"Dry-run: '{spec.name}' NO se ha escrito. Esto es lo que generaría "
                    f"({', '.join(ficheros)}).",
                    data={
                        "dry_run": True,
                        "agent": spec.name,
                        "actions": list(spec.actions),
                        "files": [{"path": r, "content": c} for r, c in ficheros.items()],
                    },
                    warnings=[_AVISO_ESQUELETO],
                )
            for rel, contenido in ficheros.items():
                rutas[rel].parent.mkdir(parents=True, exist_ok=True)
                rutas[rel].write_text(contenido, encoding="utf-8")
        finally:
            self._desregistrar(spec.name)

        # En producción el módulo ya está en agents/external/, así que el
        # descubrimiento lo importa de verdad; en un contexto de test sobre
        # tmp_path no hay nada que importar y vale la clase ya ejecutada.
        agent_registry.discover(force=True)
        if spec.name not in agent_registry.all():
            register_agent(clase)

        problemas_contrato = validate_contracts(set(agent_registry.all()))
        return AgentResult(
            True, self.name, "scaffold",
            f"Agente '{spec.name}' generado y registrado: {', '.join(ficheros)}.",
            data={
                "agent": spec.name,
                "actions": list(spec.actions),
                "files": list(ficheros),
                "registered": spec.name in agent_registry.all(),
                "contract_problems": problemas_contrato,
            },
            warnings=[_AVISO_ESQUELETO] + problemas_contrato,
        )

    def list_installed(self) -> AgentResult:
        external_dir = self.ctx.root / "agents" / "external"
        files = [
            p.name for p in external_dir.glob("*.py")
            if p.name not in ("__init__.py",) and not p.name.startswith("_")
        ]
        return AgentResult(True, self.name, "list_installed", f"{len(files)} agente(s) externo(s) instalado(s).", data=files)

    def verify(self, *, agent_name: str) -> AgentResult:
        agent_registry.discover(force=True)
        if agent_name not in agent_registry.all():
            return AgentResult(
                False, self.name, "verify",
                f"'{agent_name}' no está registrado. Revisa que el archivo esté en agents/external/ o agents/agents/ "
                f"y que la clase tenga @register_agent con name='{agent_name}'.",
            )
        agent_cls = agent_registry.get(agent_name)
        instance = agent_cls(context=self.ctx)
        return AgentResult(True, self.name, "verify", f"'{agent_name}' registrado y operativo.", data=instance.describe())
