class PaymentGateway:
    """Simulated external payment processor"""

    def process_payment(self, patron_id, amount):
        # Stripe/PayPal
        raise NotImplementedError("External payment gateway not available.")

    def refund_payment(self, transaction_id, amount):
        raise NotImplementedError("External payment gateway not available.")