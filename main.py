from turtle import end_fill
from flask import Flask, request, render_template, redirect
import psycopg2
app = Flask(__name__)

conn = psycopg2.connect(user="postgres", password="Alili4040", host="localhost", port="5432", database="myduka")
cur =conn.cursor()

@app.route('/')
def index():
    username = "Techcamp Kenya"
    return render_template("index.html", name = username)

@app.route('/inventory', methods=["POST","GET"])
def inventory():
     
    if request.method=="POST":
        productname = request.form["pname"] 
        buyingprice = request.form["bprice"]
        sellingprice = request.form["sprice"]
        quantity = request.form["quantity"]

        print(productname)
        print(buyingprice)  
        print(sellingprice)
        print(quantity)

        cur.execute("""insert into products(name, buyingprice, sellingprice, quantity) values (%(productname)s,%(buyingprice)s,%(sellingprice)s,%(quantity)s)""", {'productname':productname,'buyingprice':buyingprice,'sellingprice':sellingprice,'quantity':quantity})
        return redirect('/')
    else:
        cur.execute("select * from products")
        data = cur.fetchall()

        return render_template("inventories.html", dt = data)

@app.route("/sales",methods=["GET","POST"])
def sales():
    if request.method =="post":
        pid= request.form["pid"]
        quantity =request.form["quantity"]
        created_at=request.form["dates"]
        cur.execute("""INSERT INTO sales (pid,quantity,created_at) values(%(pid)s,%(quantity)s,%(created_at)s """, {
            'pid': pid,'quantity':quantity, 'created_at' : created_at })
    else:
        cur.execute("select * from sales")
        data = cur.fetchall()
        print(data)
        return render_template("sales.html" , data=data)



@app.route('/make_sale' ,methods=['GET' ,'POST'])
def make_sale():
    pid =request.form['pid']
    quantity=request.form['quantity']
    created_at= "NOW()" #time when the sale is made
    t = (pid, quantity, created_at)
    cur.execute("SELECT quantity FROM products where id = %s",pid)
    stock_quantity = cur.fetchone()
    print(stock_quantity)
    if stock_quantity[0] <=0 :
        pass
    else:
        stock_quantity= int(stock_quantity[0])
        quantity = int(quantity)
        remaining_stock = stock_quantity - quantity
        cur.execute("""update products set quantity=%(remaining_stock)s where id=%(pid)s""", {"pid": pid, "remaining_stock":remaining_stock})
        cur.execute("INSERT INTO sales (pid, quantity, created_at) VALUES (%s, %s, %s)",t)

        #commit changes you make to the database

        conn.commit()
        return redirect('/inventory')
@app.route('/dashboard')
def dashboard():    
    cur.execute("select count(id) from products")
    total_sales = cur.fetchone()
    cur.execute("select count(id) from sales")    
    total_products = cur.fetchone()    
    print(total_products)
    cur.execute('select sum((products.sellingprice - products.buyingprice) * sales.quantity) as profit, products.name from sales join products on products.id=sales.pid GROUP BY products.name')
    graph = cur.fetchall()
    product_name=[]
    profit=[]
    for i in graph:
        product_name.append(i[1])
        profit.append(i[0])
    return render_template('dashboard.html',total_products = total_products[0], total_sales = total_sales[0], product_name = product_name,profit=profit)

if __name__ == '__main__':
    app.run()

    