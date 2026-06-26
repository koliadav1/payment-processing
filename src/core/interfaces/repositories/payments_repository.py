from src.models.payments import Payment
from .base_repository import IRepository


class IPaymentsRepository(IRepository[Payment]):
    pass
