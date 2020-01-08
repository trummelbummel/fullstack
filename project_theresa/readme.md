# readme for item catalog 

***Prerequisites:***

To run the app one has to generate an client secret at the google web developer. 
This client secret has to be downloaded and named `client_secret.json` and made 
available to the application in the applications root directory `./project_theresa`.
Then the secret key needs to be changed at the bottom of the file `finalProject.py`.

First unzip the files and put the project_theresa folder into the /vagrant 
subdirectory.

The application is run using:
```
cd /vagrant/project_theresa
python finalProject.py
```

***The appliation enables the following:***

When logged out:
```
- login 
- view latest added items
- view items in categories 
- view categories
```

When logged in additionally these use cases can be done:
```
- creating a new item 
- delete an item and confirming the deletion
- edit (update) an already existing item
- logout
```

Please note: although I have used the string version of the category in the urls I 
have decided against using the String version of the Item name as duplicate item 
names under the same name would lead to a situation where the item would not be 
distinguishable if all other parameters except the price are the same. 

***The API endpoint implements two functionalities***

```
1. retrieve all categories and items, using the request 
curl localhost:8000/get_categories/
2. retrieve an arbitrary item in the catalog, providing the name of an item
curl localhost:8000/get_iteminfo/<string:item>   
```
here use e.g. trouser as item if you have the item trouser in your database.
It will retrieve all items and all category information which contain the item trouser.