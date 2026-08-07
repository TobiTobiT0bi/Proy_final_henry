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

def display_metrics(metrics: dict):
     if metrics.get("valid"):
          cat = metrics["selected_category"].upper()
          console.print(
               f"\n[bold magenta]🏷️  Tipo de Golden Case Seleccionado:[/bold magenta] [bold yellow]{cat}.json[/bold yellow]"
               f"(Iterando sobre sus 5 casos internos)"
          )

          cases_table = Table(title=f"Evaluacion interna ({cat}.json)", show_header=True)
          cases_table.add_column("Caso ID", style="cyan")
          cases_table.add_column("Accuracy", style="yellow", justify="right")
          cases_table.add_column("Completeness", style="green", justify="right")
          
          for case_item in metrics["cases_detailed"]:
               cases_table.add_row(
                    f"Case: {case_item['id']}",
                    f"{case_item['accuracy']:.2f}",
                    f"{case_item['completeness']:.2f}",
               )

          console.print(cases_table)

          avg_acc = metrics["avg_accuracy"]
          avg_comp = metrics["avg_completeness"]
          console.print(
            Panel(
                f"[bold white]Resumen ({cat}.json):[/bold white] Accuracy Promedio [bold yellow]{avg_acc:.2f}[/bold yellow] | "
                f"Completeness Promedio [bold green]{avg_comp:.2f}[/bold green]",
                border_style="magenta",
            )
        )
     else:
        err_msg = metrics.get("error", "Error en evaluación")
        console.print(Panel(f"[bold red]Evaluación Golden Cases:[/bold red] N/A ({err_msg})"))

def display_results(result: ContractChangeOutput):
     """Muestra los resultados del análisis en tablas y paneles formateados."""
     console.print("\n")
     console.print(
          Panel("[bold green]ANALISIS DE ENMIENDA COMPLETADO CON EXITO[/bold green]")
     )

     table = Table(title="Resultados estructurados", show_header=True)
     table.add_column("Propiedad", style="cyan", width=25)
     table.add_column("Detalle / Valor", style="white")

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
               resultado, metrics = pipeline_runner(orig_path, amen_path)
               display_results(resultado)
               display_metrics(metrics)

          except Exception as e:
               console.print(
                    f"\n[bold red]Error durante la ejecucion del pipeline:[/bold red] {e}"
               ) 

          input("\nPresiona [ENTER] para volver al menu principal...")