import os 
import sys
import questionary
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.models import ContractChangeOutput

console = Console()
TEST_DATA_DIR = Path("data/test_contracts")

def clear_screen():
    """Limpia la pantalla de la consola según el SO."""
    os.system("cls" if os.name == "nt" else "clear")

def get_available_pairs() -> dict[str, tuple[str, str]]:
     """Detecta de forma dinámica los pares de documentos en data/test_contracts/."""
     if not TEST_DATA_DIR.exists():
          return {}
     
     pairs = {}
     for file in TEST_DATA_DIR.glob("*.jpg"):
          name = file.name
          if "__original.jpg" in name:
               prefix = name.replace("__original.jpg", "")
               amendment_file = TEST_DATA_DIR / f"{prefix}__enmienda.jpg"
               if amendment_file.exists():
                    pairs[prefix] = (str(file), str(amendment_file))

     return pairs

def display_results(result: ContractChangeOutput):
     """Muestra los resultados del análisis en tablas y paneles formateados."""
     console.print("\n")
     console.print(
          Panel("[bold green]ANALISIS DE ENMIENDA COMPLETADO CON EXITO[/bold green]")
     )

     table = Table(title="Resultados estructurados", show_header=True)
     table.add_column("Propiedad", style="cyan", width=25)
     table.add_column("Detalle / Valor", syle="white")

     table.add_row("Secciones modificadas", ", ".join(result.sections_changed))
     table.add_row("Tópicos afectados", ", ".join(result.topics_touched))

     console.print(table)

     console.print(
          Panel(
               result.summary_of_the_change,
               title="[bold yellow]Resumen detallado del cambio[/bold yellow]",
               expand=False,
          )
     )

def select_preset_pair_menu() -> tuple[str, str] | None:
     clear_screen()
     pairs = get_available_pairs()

     if not pairs:
          console.print("[bold red]No se encontraron pares de archivos __original.jpg y __enmienda.jpg en data/test_contracts/[/bold red]")
          input("\nPresiona [ENTER] para regresar...")
          return None
     
     choices = [f"{prefix} (Original vs. Enmienda)" for prefix in pairs.keys()]
     choices.append("⬅️ Volver atras")

     selection = questionary.select(
          "Selecciona el par de documentos a comparar:",
          choices=choices,
     ).ask()

     if not selection or selection == "⬅️ Volver atras":
          return None
     
     prefix = selection.split(" ")[0]
     return pairs[prefix]

def custom_paths_menu() -> tuple[str, str] | None:
     """Menu para ingresar rutas personalizadas manualmente"""
     clear_screen()
     console.print(
          Panel("Ingreso de rutas personalizadas")
     )

     orig = questionary.path(
          "Ruta del contrato ORIGINAL (.jpg):",
          default="data/test_contracts/documento_1__original.jpg",
     ).ask()

     if not orig:
          return None
     
     amen = questionary.path(
          "Ruta de la ENMIENDA (.jpg): ",
          default="data/test_contracts/documento_1__enmienda.jpg",
     ).ask()

     if not amen:
          return None
     
     return orig, amen

def run_interactive_menu(pipeline_runner):
     """Muestra el menú principal y delega la ejecución al callback del pipeline."""
     while True:
          clear_screen()
          console.print(
               Panel.fit(
                    "[bold cyan]SISTEMA DE ANALISIS DE ENMIENDAS CONTRACTUALES CON IA[/bold cyan]"
                    "[dim] Auditoria automatizada usando GPT-4o Vision + Agentes en pipeline[/dim]",
                    border_style="cyan",
               )
          )

          option = questionary.select(
               "¿Que deseas hacer?",
               choices=[
                    "📁 Seleccionar par de prueba existente (data/test_contracts/)",
                    "✏️  Ingresar rutas de imágenes manualmente",
                    "🚪 Salir",
               ]
          ).ask()

          paths = None
          if option == "📁 Seleccionar par de prueba existente (data/test_contracts/)":
              paths = select_preset_pair_menu()
          elif option == "✏️  Ingresar rutas de imágenes manualmente":
              paths = custom_paths_menu()
          elif option == "🚪 Salir" or option is None:
              clear_screen()
              console.print("[bold green]¡Hasta luego![/bold green]")
              sys.exit(0)

          if paths:
               orig_path, amen_path = paths
               clear_screen()
               console.print(
                    Panel(
                         f"[bold yellow]Procesando:[/bold yellow]\n• Original: {orig_path}\n• Enmienda: {amen_path}",
                         title = "Pipeline de auditoria contractual",
                    )
               )

          try:
               resultado = pipeline_runner(orig_path, amen_path)
               display_results(resultado)

          except Exception as e:
               console.print(
                    f"\n[bold red]Error durante la ejecucion del pipeline:[/bold red] {e}"
               ) 

          input("\nPresiona [ENTER] para volver al menu principal...")