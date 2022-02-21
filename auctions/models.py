from audioop import reverse
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE, PROTECT



class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    watchlist = models.ManyToManyField('ActiveListings', blank=True, related_name="user")
    

    def __str__(self):
        return self.username


    def get_watchlist(self):
       return self.watchlist
    
class Category(models.Model):
    name=models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.name


class ActiveListings(models.Model):
    lot_name=models.CharField(max_length=150, verbose_name='Назва товару')
    slug = models.SlugField(max_length=150, unique=True, blank=True, verbose_name="URL", null=True)
    lot_author = models.ForeignKey(User, on_delete=CASCADE, null=True)
    lot_image = models.ImageField(upload_to="images/%Y/%m/%d/", verbose_name="Фото", blank=True)
    lot_description = models.TextField(verbose_name="Опис")
    price = models.DecimalField(max_digits=50, decimal_places=2, null=True, default=0, verbose_name="Початкова ставка, $")
    start_bet = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True, default=0, verbose_name="Ставка, $")
    winner = models.CharField(max_length=50, verbose_name='Переможець', null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')
    cat = models.ForeignKey(Category, on_delete=PROTECT, blank=True, verbose_name='Категорія', null=True)
    is_closed = models.BooleanField(default=False, verbose_name="Закрити аукціон")

    def __str__(self):
        return f"{self.lot_name}"
                

    def get_absolut_url(self):
        return reverse("lot", kwargs={"post_pk": self.pk})


    def equal_fields(self, bet_pk):
        bet_price = Bet.objects.values('bet_price').get(pk=bet_pk)
        return self.start_bet > self.price or self.start_bet == bet_price['bet_price']

    class Meta:
        verbose_name="Товар"
        verbose_name_plural="Товари"


class Bet(models.Model):
    bet_item = models.ForeignKey(ActiveListings, on_delete=CASCADE, null=True)
    bet_price = models.DecimalField(max_digits=50, decimal_places=2, verbose_name="Ставка, $", null=True)
    last_bet_user = models.ForeignKey(User, related_name='last_bet_user', blank=True, on_delete=CASCADE, verbose_name='Хто зробив ставку', null=True)
        
    def __str__(self):
        return f"{self.bet_item}"

    def is_valid_price(self, post_pk):
        price = ActiveListings.objects.values('price').get(pk=post_pk)
        return self.bet_price > price['price']

    class Meta:
        verbose_name="Ставка"
        verbose_name_plural="Ставки"


class Comments(models.Model):
    title = models.CharField(max_length=150, verbose_name="Заголовок", default="Заголовок")
    item = models.ForeignKey(ActiveListings, on_delete=CASCADE, null=True, verbose_name='Товар')
    comment_author = models.ForeignKey(User, on_delete=CASCADE, null=True, blank=True,)
    text = models.TextField(max_length=500,  verbose_name='Текст')
    date = models.DateTimeField("Дата", auto_now_add=True)
        
    def __str__(self):
        return f"{self.item}"

    class Meta:
        verbose_name="Коментар"
        verbose_name_plural="Коментарі"


    def get_absolut_url(self):
        return reverse("add_comments", kwargs={"post_pk": self.pk})
    

