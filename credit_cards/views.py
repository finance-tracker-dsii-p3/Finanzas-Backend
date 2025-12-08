from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from credit_cards.models import InstallmentPlan, InstallmentPayment
from credit_cards.serializers import (
    InstallmentPlanSerializer,
    InstallmentPlanCreateSerializer,
    InstallmentPaymentRecordSerializer,
)
from credit_cards.services import InstallmentPlanService


class InstallmentPlanViewSet(viewsets.GenericViewSet):
    queryset = InstallmentPlan.objects.all()
    serializer_class = InstallmentPlanSerializer

    def get_queryset(self):
        return InstallmentPlan.objects.filter(user=self.request.user).select_related(
            "credit_card_account", "financing_category", "purchase_transaction"
        ).prefetch_related("payments")

    def list(self, request):
        serializer = InstallmentPlanSerializer(self.get_queryset(), many=True)
        return Response({"status": "success", "data": {"count": len(serializer.data), "results": serializer.data}})

    def create(self, request):
        serializer = InstallmentPlanCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        plan = InstallmentPlanService.create_from_transaction(
            purchase_transaction=data["purchase_tx"],
            number_of_installments=data["number_of_installments"],
            interest_rate=data["interest_rate"],
            start_date=data.get("start_date") or timezone.now().date(),
            financing_category=data["financing_category_obj"],
            description=data.get("description", ""),
        )
        return Response({"status": "success", "data": {"plan_id": plan.id}}, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        plan = self.get_object()
        serializer = InstallmentPlanSerializer(plan)
        return Response({"status": "success", "data": serializer.data})

    def partial_update(self, request, pk=None):
        plan = self.get_object()
        updated = InstallmentPlanService.update_plan(
            plan,
            number_of_installments=request.data.get("number_of_installments"),
            interest_rate=request.data.get("interest_rate"),
            start_date=request.data.get("start_date"),
            description=request.data.get("description"),
        )
        serializer = InstallmentPlanSerializer(updated)
        return Response({"status": "success", "data": serializer.data})

    @action(detail=True, methods=["get"], url_path="schedule")
    def schedule(self, request, pk=None):
        plan = self.get_object()
        schedule = plan.get_payment_schedule()
        return Response({"status": "success", "data": {"schedule": schedule}})

    @action(detail=True, methods=["post"], url_path="payments")
    def record_payment(self, request, pk=None):
        plan = self.get_object()
        serializer = InstallmentPaymentRecordSerializer(
            data=request.data, context={"request": request, "plan": plan}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        payment, transfer_tx, interest_tx = InstallmentPlanService.record_payment(
            plan=plan,
            installment_number=data["installment_number"],
            payment_date=data["payment_date"],
            source_account=data["source_account"],
            notes=data.get("notes", ""),
        )
        return Response(
            {
                "status": "success",
                "data": {
                    "payment": {
                        "id": payment.id,
                        "status": payment.status,
                        "payment_date": payment.payment_date,
                    },
                    "transactions": {
                        "transfer_id": transfer_tx.id if transfer_tx else None,
                        "interest_id": interest_tx.id if interest_tx else None,
                    },
                },
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"], url_path="monthly-summary")
    def monthly_summary(self, request):
        year = int(request.query_params.get("year", timezone.now().year))
        month = int(request.query_params.get("month", timezone.now().month))
        summary = InstallmentPlanService.get_monthly_summary(request.user, year, month)
        return Response({"status": "success", "data": summary})

    @action(detail=False, methods=["get"], url_path="upcoming-payments")
    def upcoming_payments(self, request):
        days = int(request.query_params.get("days", 30))
        payments = InstallmentPlanService.get_upcoming_payments(request.user, days)
        data = [
            {
                "plan_id": p.plan_id,
                "installment_number": p.installment_number,
                "due_date": p.due_date,
                "installment_amount": p.installment_amount,
                "status": p.status,
                "credit_card": p.plan.credit_card_account.name,
            }
            for p in payments
        ]
        return Response({"status": "success", "data": data})
