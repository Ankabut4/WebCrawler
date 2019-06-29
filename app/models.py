"""
Definition of models.
"""

from django.db import models

# Crea  te your models here.
class Record(models.Model):
    id = models.AutoField(primary_key=True)
    county = models.CharField(max_length=50)
    address = models.CharField(max_length=250)
    sale_date = models.CharField(max_length=160)
    case = models.CharField(max_length=90)
    courtsp = models.CharField(max_length=90)
    bid = models.CharField(max_length=250)
    status=models.BooleanField(default=True)
    site= models.CharField(max_length=200)
    comment = models.CharField(max_length=250,default='Pending')
    def as_json(self):
        return dict(id=self.id, county=self.county, address=self.address, sale_date=self.sale_date, case=self.case, courtsp=self.courtsp, bid=self.bid, status=self.status, site=self.site, comment=self.comment)