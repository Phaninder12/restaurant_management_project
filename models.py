from django.db import models # type: ignore

# Create your models here.
class Item(models.Model):
    item_name = models.CharField(max_length=150)
    item_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.item_name)

class NutritionalInformation(models.Model):
    # Link to the Item model defined above
    menu_item = models.ForeignKey(
        Item, 
        on_delete=models.CASCADE,
        related_name='nutritional_info'
    )
    
    # Nutritional data fields
    calories = models.IntegerField()
    protein_grams = models.DecimalField(max_digits=5, decimal_places=2)
    fat_grams = models.DecimalField(max_digits=5, decimal_places=2)
    carbohydrate_grams = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.menu_item.item_name} - {self.calories} kcal"    