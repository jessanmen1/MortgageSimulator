import numpy_financial as npf
from typing import Any
import os

FILE_HEADER = "month;monthly_interest;amortized_loan;pending_loan;interest;monthly_payment;accumulated_interest"
SIMULATIONS_FOLDER = "simulations"


class NaiveEuriborUpdater:
    def __init__(self, initial_value, euribor_yearly_increment) -> None:
        self.euribor_yearly_increment = euribor_yearly_increment
        self.current_euribor = initial_value

    def update_euribor_value(self) -> None:
        self.current_euribor = self.current_euribor + self.euribor_yearly_increment

    def get_euribor_value(self) -> Any:
        return self.current_euribor


class VariableRateMortgage:
    def __init__(
        self,
        differential,
        loan,
        output_file_name,
        periods=30 * 12,
        euribor_updater=NaiveEuriborUpdater(0, 0.001),
        verbose=False,
    ) -> None:
        self.differential = differential
        self.periods = periods
        self.loan = loan
        self.accumulated_interest = 0

        self.output_file_name = output_file_name
        with open(os.path.join(SIMULATIONS_FOLDER, self.output_file_name), "w") as f:
            f.write(f"{FILE_HEADER}\n")

        self.euribor_updater = euribor_updater
        self.current_month = 0
        self.interest = self.differential + euribor_updater.get_euribor_value()
        self.monthly_payment = self.calculate_monthly_cuota()
        self.verbose = verbose

    def calculate_monthly_cuota(self) -> Any:
        return (
            npf.pmt(self.interest / 12, self.periods - self.current_month, self.loan)
            * -1
        )

    def print_beatify(self, monthly_interest) -> None:
        print(
            f"mes {self.current_month}: intereses -> {monthly_interest} | prestamo amortizado -> {self.monthly_payment-monthly_interest} | pending -> {self.loan}"
        )

    def append_to_file(self, monthly_interest) -> None:
        with open(os.path.join(SIMULATIONS_FOLDER, self.output_file_name), "a") as f:
            f.write(
                f"{self.current_month};{monthly_interest};{self.monthly_payment-monthly_interest};{self.loan};{self.interest};{self.monthly_payment};{self.accumulated_interest}\n"
            )

    def simulate(self) -> None:
        for m in range(self.periods):
            self.current_month = m
            monthly_interest = self.loan * self.interest / 12
            self.accumulated_interest = self.accumulated_interest + monthly_interest
            self.loan = self.loan - (self.monthly_payment - monthly_interest)
            if self.verbose:
                self.print_beatify(monthly_interest)

            self.append_to_file(monthly_interest)
            self.periods = self.periods
            if (m + 1) % 12 == 0:
                self.euribor_updater.update_euribor_value()
                self.interest = (
                    self.differential + self.euribor_updater.get_euribor_value()
                )
                self.monthly_payment = self.calculate_monthly_cuota()
                if self.verbose:
                    print(
                        f"new interest -> {self.interest} | new cuota -> {self.monthly_payment} | intereses pagados hasta ahora -> {self.accumulated_interest}"
                    )


class FixedRateMortgage:
    def __init__(
        self,
        interest,
        loan,
        output_file_name,
        periods=30 * 12,
        verbose=False,
    ) -> None:
        self.interest = interest
        self.periods = periods
        self.loan = loan
        self.accumulated_interest = 0

        self.output_file_name = output_file_name
        with open(os.path.join(SIMULATIONS_FOLDER, self.output_file_name), "w") as f:
            f.write(f"{FILE_HEADER}\n")

        self.current_month = 0
        self.monthly_payment = self.calculate_monthly_cuota()
        self.verbose = verbose

    def calculate_monthly_cuota(self) -> Any:
        return (
            npf.pmt(self.interest / 12, self.periods - self.current_month, self.loan)
            * -1
        )

    def print_beatify(self, monthly_interest) -> None:
        print(
            f"mes {self.current_month}: intereses -> {monthly_interest} | prestamo amortizado -> {self.monthly_payment-monthly_interest} | pending -> {self.loan}"
        )

    def append_to_file(self, monthly_interest) -> None:
        with open(os.path.join(SIMULATIONS_FOLDER, self.output_file_name), "a") as f:
            f.write(
                f"{self.current_month};{monthly_interest};{self.monthly_payment-monthly_interest};{self.loan};{self.interest};{self.monthly_payment};{self.accumulated_interest}\n"
            )

    def simulate(self) -> None:
        for m in range(self.periods):
            self.current_month = m
            monthly_interest = self.loan * self.interest / 12
            self.accumulated_interest = self.accumulated_interest + monthly_interest
            self.loan = self.loan - (self.monthly_payment - monthly_interest)
            if self.verbose:
                self.print_beatify(monthly_interest)

            self.append_to_file(monthly_interest)


if __name__ == "__main__":

    loan = 200_000

    # euribor_updater = NaiveEuriborUpdater(
    #    initial_value=-0.00558, euribor_yearly_increment=0.001
    # )
    # mortgage1 = VariableRateMortgage(
    #    differential=0.007,
    #    loan=loan,
    #    output_file_name="class_test.txt",
    #    periods=30 * 12,
    #    euribor_updater=euribor_updater,
    # )
    # mortgage1.simulate()
    fija = FixedRateMortgage(0.01, 200_000, "fija.txt")
    fija.simulate()
