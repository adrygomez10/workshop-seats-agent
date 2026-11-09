"""Error for reports whose seats differ from the catalog."""

from workshop_seats.application.availability_report import (
    AvailabilityReport,
)


class InconsistentReportError(RuntimeError):
    """Raised when a valid report contradicts the catalog."""

    def __init__(self, report: AvailabilityReport, catalog_seats: int) -> None:
        """Describe both counts so the difference can be investigated."""
        super().__init__(
            f"The assistant reported {report.available_seats} seats for "
            f"{report.workshop_name}, but the catalog has {catalog_seats}."
        )
        self.report = report
        self.catalog_seats = catalog_seats
