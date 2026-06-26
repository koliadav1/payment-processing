from src.core.interfaces.repositories.payments_repository import (
    IPaymentsRepository,
)
from src.models.payments import Payment
from .base_repository import SQLRepository


class PaymentsRepository(IPaymentsRepository, SQLRepository):
    def __init__(self, session):
        super().__init__(session, Payment)
