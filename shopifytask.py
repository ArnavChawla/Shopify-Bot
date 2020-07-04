import os
import json
import requests
import random
from bs4 import BeautifulSoup as soup
from threading import Thread
import time
class size():
    def __init__(self,variant,sizen):
        self.variant = variant
        self.sizes = sizen
class shopifytask():
    def __init__(self,profilename,size,keyword,siteUrl):
        #print("here")
        self.status = "waiting for start"
        self.loadprofile(profilename)
        self.siteUrl = siteUrl
        self.taskKeys = keyword
        self.keywords = []
        a= keyword.split(",")
        for word in a:
            self.keywords.append(word)
        print(self.keywords)
        self.random_size = False
        self.shipping = True
        if(size != "random"):
            self.size = size
        else:
            self.random_size = True
            self.size = "random"
        self.session=requests.session()
    def loadprofile(self,profilename):
        a = open(os.getcwd()+"/profiles/"+profilename+".json")
        x = json.load(a)
        self.city = x["city"]
        self.last = x["last"]
        self.zip = x["Zip"]
        self.phone = x["phone"]
        self.cvv = x["cvv"]
        self.credit=x["credit"]
        self.state=x["state"]
        self.exp = x["exp"]
        self.address = x["address"]
        self.email = x["email"]
        self.first = x["First"]
        self.month = x["exp"].split('/')[0]
        self.year = x["exp"].split('/')[1]
    def preloadPayment(self):
        link = "https://elb.deposit.shopifycs.com/sessions"
        payload = {
            "credit_card": {
                "number": self.credit,
                "name": self.first + " " + self.last,
                "month": self.month,
                "year": self.year,
                "verification_value": self.cvv
            }
        }
        r = requests.post(link, json=payload, verify=False)
        self.payment_token = json.loads(r.text)["id"]
    def getProducts(self):
        r = self.session.get(self.siteUrl+"/products.json")
        jso = json.loads(r.text)
        jso = jso["products"]
        return jso
    def keywordSearch(self,products):
        for product in products:
            count = 0
            title = product["title"]
            #print(title)
            for key in self.keywords:
                if(key.lower() in title.lower()):
                    count += 1
            if(count == len(self.keywords)):
                self.taskKeys=title
                return product

    def findSize(self,product):
        for variant in product["variants"]:
            if(variant["requires_shipping"] == False):
                self.shipping = False
            if(self.random_size):
                variants = []
                for variant in product["variants"]:
                    print(variant)
                    variants.append(size(variant["id"],variant["title"]))
                variant = random.choice(variants)
                strv = variant.variant
                self.size = variant.sizes
                print("Shipping = " + str(self.shipping))
                return strv
            elif(self.size in variant["title"]):
                variant = str(variant["id"])
                #print(variant)
                print("Shipping = " + str(self.shipping))
                return variant
    def atc(self,productID):
        r = self.session.get(self.siteUrl+"/cart/add.js?id="+str(productID))
        r = self.session.get(self.siteUrl+"/checkout")
        self.checkoutUrl = r.url
        return  r.url
    def first_page(self):
        payload = {
        "utf8": u"\u2713",
        "_method": "patch",
        "authenticity_token": "",
        "previous_step": "contact_information",
        "step": "shipping_method",
        "checkout[email]": self.email,
        "checkout[buyer_accepts_marketing]": "0",
        "checkout[shipping_address][first_name]": self.first,
        "checkout[shipping_address][last_name]": self.last,
        "checkout[shipping_address][company]": "",
        "checkout[shipping_address][address1]": self.address,
        "checkout[shipping_address][address2]": "",
        "checkout[shipping_address][city]": self.city,
        "checkout[shipping_address][country]": "United States",
        "checkout[shipping_address][province]": self.state,
        "checkout[shipping_address][zip]": self.zip,
        "checkout[shipping_address][phone]": self.phone,
        "checkout[remember_me]": "0",
        "checkout[client_details][browser_width]": "1710",
        "checkout[client_details][browser_height]": "1289",
        "checkout[client_details][javascript_enabled]": "1",
        "button": ""
        }
        self.session.post(self.checkoutUrl,data=payload)
    def get_shipping(self):
        link = self.siteUrl + "//cart/shipping_rates.json?shipping_address[zip]={}&shipping_address[country]={}&shipping_address[province]={}".format(self.zip,"United States",self.state)
        r = self.session.get(link, verify=False)
        shipping_options = json.loads(r.text)

        ship_opt = shipping_options["shipping_rates"][0]["name"].replace(' ', "%20")
        ship_prc = shipping_options["shipping_rates"][0]["price"]

        shipping_option = "shopify-{}-{}".format(ship_opt,ship_prc)
        self.s = shipping_option
        #(self.s)
    def submit_shipping(self):
        data = {
            'utf8':u"\u2713",
            '_method':'patch',
            'authenticity_token':'',
            'previous_step':'shipping_method',
            'step':'payment_method',
            'checkout[shipping_rate][id]':self.s,
            'button':'',
            'checkout[client_details][browser_width]':'891',
            'checkout[client_details][browser_height]':'803',
            'checkout[client_details][javascript_enabled]':'1'
        }
        print("CHECKOUT: "+self.checkoutUrl)
        r = self.session.post(self.checkoutUrl,data=data)

    def checkout_gateway(self):
        r= self.session.get(self.checkoutUrl +"?step=payment_method")
        bs = soup(r.text, "html.parser")
        gatewa = bs.find("input", {"checked": "checked"})["value"]
        #print(gatewa)
        self.gateway = gatewa
    def checkout(self):
        payload = {
        "utf8": u"\u2713",
        "_method": "patch",
        "authenticity_token": "",
        "previous_step": "payment_method",
        "step": "",
        "s": self.payment_token,
        "checkout[payment_gateway]": self.gateway,
        "checkout[credit_card][vault]": "false",
        "checkout[different_billing_address]": "false",
        "complete": "1",
        "checkout[client_details][browser_width]": str(random.randint(1000, 2000)),
        "checkout[client_details][browser_height]": str(random.randint(1000, 2000)),
        "checkout[client_details][javascript_enabled]": "1",
        "g-recaptcha-repsonse": "",
        "button": ""
        }
        r = self.session.post(self.checkoutUrl+"?step=payment_method", data=payload)
        print(r.text)
        print("done")
        self.status="checked out"
    def run(self):
        self.status= "running"
        self.preloadPayment()
        self.atc(self.find_size(self.keywordSearch(self.getProducts())))
        first = Thread(target=self.first_page)
        second = Thread(target=self.get_shipping)
        third = Thread(target=self.checkout_gateway)
        start = time.time()
        first.start()
        if(self.shipping==True):
            second.start()
        third.start()
        first.join()
        if(self.shipping == True):
            second.join()
        third.join()
        if(self.shipping == True):
            self.submit_shipping()
        self.checkout()
        print(time.time()-start)
