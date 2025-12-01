class PaymentGateway:
    def process_payment(self, patron_id, amount):
        return {"status": "success", "patron_id": patron_id, "amount": amount}

    def refund_payment(self, transaction_id, amount):
        return {"status": "refunded", "transaction_id": transaction_id, "amount": amount}