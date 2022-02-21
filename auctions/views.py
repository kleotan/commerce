from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from auctions.forms import *
from django.db.models import *
from django.contrib import messages
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import Http404

def index(request):
    goods = ActiveListings.objects.all().order_by("-date_created").exclude(is_closed=True)
    cats=Category.objects.all()
    return render(request, "auctions/index.html", {
        'goods': goods,
        'cats': cats,
        "cat_selected": 0,
       
    })

def cats(request):
    return render(request, "auctions/cats.html", {
                'cats': Category.objects.all()
            })   
    

def get_category(request, cat_pk):
    goods=ActiveListings.objects.filter(cat__pk=cat_pk).exclude(is_closed=True)
    return render(request, "auctions/index.html", {
                'goods': goods,
                "c_selected": 0,
            })   

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            lot = ActiveListings.objects.filter(is_closed=True).values('winner', 'lot_name')
            for l in lot:
                if l['winner'] == request.user.username:  
                    messages.info(request, f"<H4>{l['lot_name']}</H4>")
            return redirect("index")
        
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
        
    else:
        return render(request, "auctions/login.html",{
            "log_selected": 0
        })


def logout_view(request):
    logout(request)
    return redirect("index")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return redirect("index")
    else:
        return render(request, "auctions/register.html", {
            "reg_selected": 0
        })


def pageNotFound(request, exception):
    return HttpResponseNotFound(f"<h1> Сторінку не знайдено </h1>")

def get_post(request, post_pk):
    try:
        lot = ActiveListings.objects.get(pk=post_pk)
        last_bet=Bet.objects.filter(bet_item=lot).last() 
        if last_bet: # если существует ставка по товару (по товару pk_post)
            lot.start_bet=last_bet.bet_price # заносим новую ставку в поле start_bet табл.ActiveListings
        if request.method == 'POST':
            form = SetBetForm(request.POST)
            if form.is_valid():
                item = ActiveListings.objects.values('price').get(pk=post_pk) # получаем значение поля цены товара post_pk из табл.ActiveListings
                bet_price=form.cleaned_data['bet_price'] # введенная ставка в поле формы.SetBetForm
                old_bet=Bet.objects.filter(bet_item__pk=post_pk).aggregate(res=Max('bet_price')) # max ставка (по товару pk_post) в таблице ставок Bet
                if old_bet['res']==None:
                    old_bet['res']=int(0)
                if bet_price > item['price'] and bet_price > old_bet['res']: # сравниваем ставку из поля табл.Bet с полем табл.ActiveListings И с max ставкой в табл.Bet (по товару pk_post)
                    lot.start_bet=bet_price
                    lot.save() # сохраняем новую ставку с поля bet_price в поле start_bet табл.ActiveListings
                else:       
                    messages.error(request, 'Нова ставка повинна бути більша за попередню') 
                    return redirect('lot', post_pk=lot.id)
                new_bet=form.save(commit=False)
                new_bet.last_bet_user = request.user
                lot.winner = request.user.username
                new_bet.save()
                lot.save()
                request.user.watchlist.add(lot) #якщо request.user зробив ставку автоматично додати товар до watchlist
                return redirect('lot', post_pk=lot.id)

            com_form = CommentsForm(request.POST)
            if com_form.is_valid():
                com=com_form.save(commit=False)
                com.comment_author = request.user
                com.save()
                return redirect('lot', post_pk=lot.id)
        else:
            form=SetBetForm(instance=lot, initial={'bet_item':lot})
            com_form=CommentsForm(instance=lot, initial={'item': lot})
        comments=Comments.objects.filter(item__pk=post_pk).order_by("-date")
        watchlist=User.objects.filter(watchlist__pk=post_pk)
    except ActiveListings.DoesNotExist:
        raise Http404
    return render(request, "auctions/lot.html", {
                'lot': lot,
               'form': form,
               'comments': comments,
               'com_form': com_form,
               'watchlist': watchlist
                 })
    

@login_required
def bet_list(request):
    lots = Bet.objects.filter(last_bet_user=request.user)
      #lots = Bet.objects.filter(user__id=user_id)
    return render(request, "auctions/bet_list.html", {
        "lots": lots,
        'bet_selected': 0,

   })

   
@login_required
def watchlist(request, user_id):
    user = User.objects.get(id=user_id)
    items = user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "user": user,
        "items": items,
        "w_selected": 0,
    })
              
         
@login_required
def add_Watchlist(request, item_id):
    if request.method=="POST":
        user = User.objects.get(username=request.user) 
        #user = User.objects.get(pk=user_id) 
        try:
            item = ActiveListings.objects.get(pk=item_id)
            user.watchlist.add(item)
        except ActiveListings.DoesNotExist:
            item = None
    return redirect('lot', post_pk=item_id)
    


@login_required
def del_Watchlist(request, item_id):
    if request.method=="POST":
        owner = User.objects.get(username=request.user) 
        try:
            item = ActiveListings.objects.get(pk=item_id)
            owner.watchlist.remove(item)
        except ActiveListings.DoesNotExist:
            item = None
    return redirect('lot', post_pk=item_id)


@login_required
def add_auction(request):
    if request.method=="POST":
        form=AddAuctionForm(request.POST, request.FILES)
        if form.is_valid():
            new_lot=form.save(commit=False)
            new_lot.lot_author = request.user
            new_lot.save()
            return redirect('lot', post_pk=new_lot.pk)
    else:
        form=AddAuctionForm()
    return render(request, "auctions/add_auction.html", {
            "form": form,
            "add_selected": 0
        })

@login_required
def edit_post(request, post_pk):
    item=ActiveListings.objects.get(pk=post_pk)
    if request.user==item.lot_author:
        lot= get_object_or_404(ActiveListings, pk=post_pk)
        if request.method == 'POST':
            form = AddAuctionForm(request.POST, request.FILES, instance=lot)
            if form.is_valid():
                form.save()
                return redirect('lot', post_pk=lot.pk)
        else:
            form=AddAuctionForm(instance=lot)
        return render(request, "auctions/edit.html", {
                'form': form                                        
            })
    else:
        raise Http404("Вам заборонено редагувати сторінку")
    

@login_required
def my_auctions(request, user_id):
    #user = User.objects.get(pk=user_id)
    items = ActiveListings.objects.filter(lot_author__pk=user_id)
    return render(request, "auctions/my_auctions.html", {
        "items": items,
        'my_list_selected': 0,
      
    })


@login_required
def closed(request, item_id):
    lot = ActiveListings.objects.get(pk=item_id)
    if request.method=="POST":
        if lot.is_closed == False:
            lot.is_closed=True
            lot.save()    
            return redirect('lot', post_pk=item_id)
    winner=ActiveListings.objects.values('start_bet', 'winner').get(pk=item_id)
    
    return render(request, "auctions/lot.html", {
            'winner': winner,     
            })
