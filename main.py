"""Cyber Incident Manager entry point."""

from controllers.auth_controller import AuthController
from controllers.dashboard_controller import DashboardController
from controllers.executive_dashboard_controller import ExecutiveDashboardController
from controllers.incident_controller import IncidentController
from controllers.knowledge_controller import KnowledgeController
from controllers.search_controller import SearchController
from database.init_db import initialize_database
from runtime_tkinter import configure_tkinter_runtime


def main() -> None:
    configure_tkinter_runtime()
    from views.dashboard_view import CyberIncidentManagerApp

    database = initialize_database()
    app = CyberIncidentManagerApp(
        auth_controller=AuthController(database),
        incident_controller=IncidentController(database),
        dashboard_controller=DashboardController(database),
        search_controller=SearchController(database),
        executive_dashboard_controller=ExecutiveDashboardController(database),
        knowledge_controller=KnowledgeController(database),
    )
    app.mainloop()


if __name__ == "__main__":
    main()
