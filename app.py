#Simeiwsi:
#Kata tin ektelesi, opoudipote ziteitai input string (diladi sta review_id,business_id) tha prepei na eisaxthei XWRIS quotes "",''.

import settings
import sys,os
sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0], 'lib'))
import pymysql as db

def connection():
    # Use this function to create your connections
    con = db.connect(
        settings.mysql_host, 
        settings.mysql_user, 
        settings.mysql_passwd, 
        settings.mysql_schema)
    
    return con
    
    
def extract_ngrams(text,n):
    
    #create word by word list
    wbw = []
    for word in text.split():
        wbw.append(word)
        
    if n == 1:
        return wbw
    
    #create ngrams list 
    ngrams = []
    
    #get all sets of 2 or 3 adjacent elements of the word by word list
    if n == 2:
        for i in range(0, (len(wbw) - 2)):
            ngrams.append(wbw[i] + ' ' + wbw[i+1])
    elif n == 3:
        for i in range(0, (len(wbw) - 3)):
            ngrams.append(wbw[i] + ' ' + wbw[i+1] + ' ' + wbw[i+2])
            
    return ngrams


def classify_review(reviewid):
    
    # Create a new connection
    con=connection()
    # Create a cursor on the connection
    cur=con.cursor()
    
    #get review text
    sql = "SELECT text FROM reviews WHERE review_id = '%s'" % (reviewid)
    try:
        cur.execute(sql)
        #Get text record from the database
        records = cur.fetchone()
    except:
        return [("result", "Data Fetch Error")]
    
    #Test review id input
    if records is None:
        return [("result", "Review ID Error")]
        
    #Get the string text from the record in variable text
    text = records[0]
    
    #Start with the positive terms in review text
    sql = "SELECT word FROM posterms"
    try:
        cur.execute(sql)
        #Get records from database 
        records = cur.fetchall()
    except:
        return [("result", "Data Fetch Error")]
        
    CP = 0 #Classifying Points, starting with value 0
        
    #First check for positive phrases with 3 words
    phrases = extract_ngrams(text,3)
    for i in range(0, (len(phrases)-1)):
        for row in records:
            #if you find a 3word positive phrase in the phrases list,
            if row[0] == phrases[i]:
                #skip 2 blocks in order not to check blocks that include the same words,
                i+=2
                #remove those words from the text so that they won't be counted in the future,                
                text.replace(phrases[i],"")
                #add 3 classifying points to the review                
                CP+=3
                break
    
    #Next check for positive phrases with 2 words from the updated text
    phrases = extract_ngrams(text,2)
    for i in range(0, (len(phrases)-1)):
        for row in records:
            #if you find a 2word positive phrase in the phrases list,
            if row[0] == phrases[i]:
                #skip 1 block in order not to check blocks that include the same words,
                i+=1
                #remove those words from the text so that they won't be counted in the future
                text = text.replace(phrases[i],"")
                #add 2 classifying points to the review
                CP+=2
                break
    
    #Finally check for positive phrases with 1 word from the updated text
    phrases = extract_ngrams(text,1)
    for i in range(0, (len(phrases)-1)):
        for row in records:
            #if you find a 1word positive phrase in the phrases list,
            if row[0] == phrases[i]:
                #remove the word from the text so that it won't be counted in the future
                text = text.replace(phrases[i],"")
                #add 1 classifying point to the review
                CP+=1
                break
    
    
    
    #Continute with the negative terms in review text
    sql = "SELECT word FROM negterms"
    try:
        cur.execute(sql)
        #Get records from database 
        records = cur.fetchall()
    except:
        return [("result", "Data Fetch Error")]
        
    #First check for negative phrases with 3 words
    phrases = extract_ngrams(text,3)
    for i in range(0, (len(phrases)-1)):
        for row in records:
            #if you find a 3word negative phrase in the phrases list,
            if row[0] == phrases[i]:
                #skip 2 blocks in order not to check blocks that include the same words,
                i+=2
                #remove those words from the text so that they won't be counted in the future,                
                text.replace(phrases[i],"")
                #subtract 3 classifying points from the review                
                CP-=3
                break
                
    #Next check for negative phrases with 2 words from the updated text
    phrases = extract_ngrams(text,2)
    for i in range(0, (len(phrases)-1)):
        for row in records:
            #if you find a 2word negative phrase in the phrases list,
            if row[0] == phrases[i]:
                #skip 1 block in order not to check blocks that include the same words,
                i+=1
                #remove those words from the text so that they won't be counted in the future
                text = text.replace(phrases[i],"")
                #subtract 2 classifying points from the review  
                CP-=2
                break
                
    #Finally check for negative phrases with 1 word from the updated text
    phrases = extract_ngrams(text,1)
    for i in range(0, (len(phrases)-1)):
        for row in records:
            #if you find a 1word negative phrase in the phrases list,
            if row[0] == phrases[i]:
                #remove the word from the text so that it won't be counted in the future
                text = text.replace(phrases[i],"")
                #subtract 1 classifying point from the review  
                CP-=1
                break
        
    #Classify review based on points
    if CP > 0:
        verdict = "Positive: " + str(CP)
    elif CP == 0:
        verdict = "Neutral: " + str(CP)
    else:
        verdict = "Negative: " + str(CP)
    
    #get business name
    sql = "SELECT b.name FROM reviews r, business b WHERE b.business_id = r.business_id AND review_id = '%s'" % (reviewid)
    try:
        cur.execute(sql)
        #Get record from the database
        records = cur.fetchone()
    except:
        return [("result", "Data Fetch Error")]
    
    #End Connection
    con.close()

    return [("business_name","result"),(records[0],verdict)]


def updatezipcode(business_id,zipcode):
    
    #Test zipcode input
    try:
        zipcode = int(zipcode)
    except:
        return [("result", "Zipcode Input Error")]
        
    # Create a new connection
    con=connection()
    # Create a cursor on the connection
    cur=con.cursor()
    
    sql = "SELECT * FROM business WHERE business_id = '%s'" % (business_id) 
    
    # Execute the SQL command
    cur.execute(sql)
    result = cur.fetchone()
    #Test Business ID input
    if result is None:
        return [("result", "Business ID Input Error")]
        
    sql = "UPDATE business SET zip_code = %d WHERE business_id = '%s'" % (zipcode, business_id)
    
    try:
        # Execute the SQL command
        cur.execute(sql)
        # Commit your changes in the database
        con.commit()
    except:
        return [("result", "Update Error")]
        
    #End Connection
    con.close()
    
    return [("result"),("OK")]
 
    

def selectTopNbusinesses(category_id,n):

    # Create a new connection
    con=connection()
    # Create a cursor on the connection
    cur=con.cursor()
    
    #Test Category ID input
    try:
        category_id = int(category_id)
        n = int(n)
    except:
        return [("result", "Input Error")]
        
    #Category IDs have values 1 through 727 and N needs to be a positive number
    if category_id < 1 or category_id > 727 or n < 0:
        return [("result", "Input Error")]
    
    #sql SELECT: Returns table of 2 rows: business id, number of positive reviews of the given category
    #ordered by descending number of positive reviews.
    sql = "SELECT b.business_id, COUNT(pn.positive) FROM business b, reviews_pos_neg pn, reviews r, business_category bc WHERE b.business_id = r.business_id AND r.review_id = pn.review_id AND bc.business_id = b.business_id AND bc.category_id = %d AND pn.positive = 1 GROUP BY business_id ORDER BY COUNT(pn.positive) DESC;" % (category_id)
    
    try:
        # Execute the SQL command
        cur.execute(sql)
    except:
        return ("result","Data Fetch Error")
        
    #Fetch the top N records selected by the SQL command
    records = cur.fetchmany(n)
    
    #Create a list results that stores the records
    results = [("Business ID", "Number of Reviews")]
    for row in records:
        results.append(row)
        
    #End Connection
    con.close()
    
    return results


def traceUserInfuence(userId,depth):
    # Create a new connection
    con=connection()

    # Create a cursor on the connection
    cur=con.cursor()



    #End Connection
    con.close()
    
    return [("user_id",),]

