from django.db.models import Aggregate, FloatField


class Percentile(Aggregate):
    function = "PERCENTILE_CONT"
    name = "percentile"
    output_field = FloatField()
    template = (
        "%(function)s (%(percentile)s) WITHIN GROUP (ORDER BY %(expressions)s)"
    )
