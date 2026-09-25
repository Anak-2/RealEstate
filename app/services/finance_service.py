from dataclasses import dataclass

@dataclass(frozen=True)
class FinanceProfile:
    cash: int = 0
    company_loan_limit: int = 0
    company_loan_balance: int = 0
    mortgage_limit: int = 0
    emergency_cash: int = 0

def buying_power(profile: FinanceProfile) -> int:
    usable_cash = max(0, profile.cash - profile.emergency_cash)
    available_company_loan = max(0, profile.company_loan_limit - profile.company_loan_balance)
    return usable_cash + available_company_loan + max(0, profile.mortgage_limit)
