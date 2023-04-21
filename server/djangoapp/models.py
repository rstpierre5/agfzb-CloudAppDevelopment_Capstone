from django.db import models
from django.utils.timezone import now


# Create your models here.

# - Name
# - Description
# - Any other fields you would like to include in car make model
# - __str__ method to print a car make object
class CarMake(models.Model):
        Name = models.CharField(null=False, max_length=100, default='Model')
        Description = models.CharField(max_length=500)

        def __str__(self):
            return "Name: " + self.Name + "," + \
                "Description: " + self.Description


# - Many-To-One relationship to Car Make model (One Car Make has many Car Models, using ForeignKey field)
# - Name
# - Dealer id, used to refer a dealer created in cloudant database
# - Type (CharField with a choices argument to provide limited choices such as Sedan, SUV, WAGON, etc.)
# - Year (DateField)
# - __str__ method to print a car make object
# Course model
class CarModel(models.Model):
    Name = models.CharField(null=False, max_length=100, default='Car')
   
    DealerId = models.IntegerField()

    # Many-To-One relationship with Car Make model
    car_make = models.ForeignKey(CarMake, null=False, on_delete=models.CASCADE)
    
    SEDAN = 'sedan'
    SUV = 'suv'
    WAGON = 'wagon'
    TRUCK = 'truck'
    CAR_CHOICES = [
        (SEDAN, 'Sedan'),
        (SUV, 'Suv'),
        (WAGON, 'Wagon'),
        (TRUCK, 'Truck')
    ]
    Type = models.CharField(
        null=False,
        max_length=20,
        choices=CAR_CHOICES,
        default=SEDAN
    )

    Year = models.DateField(null=True)


    # Create a toString method for object string representation
    def __str__(self):
        return "Name: " + self.Name + "," + \
            "Dealer ID: " + str(self.DealerId) + "," + \
            "Car Type: " + self.Type


# <HINT> Create a plain Python class `CarDealer` to hold dealer data


# <HINT> Create a plain Python class `DealerReview` to hold review data
