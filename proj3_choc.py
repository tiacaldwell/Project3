''''
Tia Caldwell 
tiacc
Project 3 
'''
# proj3_choc.py
# You can change anything in this file you want as long as you pass the tests
# and meet the project requirements! You will need to implement several new
# functions.

# Part 1: Read data from a database called choc.db
import sqlite3
from tabulate import tabulate
import plotly
import plotly.graph_objs as go 

DBNAME = 'choc.sqlite'
conn = sqlite3.connect(DBNAME)
handle = conn.cursor()

# Part 1: Implement logic to process user commands
def sell_or_source(command):
    ''' 
    Parameters
    ----------
    command: string
        The user-entered command for sql access 

    Returns
    -------
    string
        a section of string that helps build the sql query 
        based on whether the user is interested in the 
        country the cholate is grown in (soruced) or sold in
    '''
    if "source" in command: 
        return "ON Bars.BroadBeanOriginId=Countries.Id"
    else: 
        return "ON Bars.CompanyLocationId=Countries.Id"

def area_limit(command): 
    ''' 
    Parameters
    ----------
    command: string
        The user-entered command for sql access 

    Returns
    -------
    string
        a section of string that helps build the sql query 
        for the WHERE clause 
    '''
    if command.find("region=") != -1:
        return " WHERE COUNTRIES.Region = " +"'" + command.split("region=",1)[1].split()[0] +"'"
    if command.find("subregion=") != -1:
        return " WHERE COUNTRIES.Region = " +"'"+ command.split("subregion=",1)[1].split()[0] +"'"
    if command.find("country=") != -1:
        return " WHERE COUNTRIES.Alpha2 = " +"'" + command.split("country=",1)[1].split()[0] +"'"
    else: return ""

def sorting(command): 
    ''' 
    Parameters
    ----------
    command: string
        The user-entered command for sql access 

    Returns
    -------
    string
        a section of string that helps build the sql query 
        for the sorting 
    '''
    if command.find("number_of_bars") != -1:
        return " ORDER BY COUNT(*)"
    if command.find("cocoa") != -1:
        return " ORDER BY CocoaPercent"
    else: 
        return " ORDER BY RATING"

def sort_top(command):
    ''' 
    Parameters
    ----------
    command: string
        The user-entered command for sql access 

    Returns
    -------
    string
        a section of string that helps build the sql query 
        for the sort order 
    '''
    if "bottom" in command: 
        return ""
    else: 
        return " DESC"

def limit(command): 
    if any(char.isdigit() for char in command): 
        number = [(char) for  char in command.split() if char.isdigit()]
        return " LIMIT " + number[0]
    else: 
        return " LIMIT 10" 

def aggregators(command): 
    ''' 
    Parameters
    ----------
    command: string
        The user-entered command for sql access 

    Returns
    -------
    string
        a section of string that helps build the sql query 
        for commands that request aggregate stats about  bars 
    '''
    if command.find("number_of_bars") != -1:
        return " COUNT(*)"
    if command.find("cocoa") != -1: 
        return " AVG(CocoaPercent) "
    else: 
        return " AVG(Rating) "

def bars(command):
    '''
    uses other functions to parse user input into an sql query 
    sends the sql query and returns the resuls 
    works only for queries about bars 

    Parameters
    ----------
    command: string
        The user-entered command for sql access 

    Returns
    -------
    tuple
        sql query results 
    '''
    if "source" in command: 
        query = ("SELECT SpecificBeanBarName, Company, comploc.EnglishName as company_location, Rating, CocoaPercent, Countries.EnglishName as source_location " 
            + "FROM BARS JOIN Countries ON Bars.BroadBeanOriginId= Countries.Id JOIN Countries comploc ON Bars.CompanyLocationId= comploc.Id "
            + area_limit(command) + sorting(command) + sort_top(command) + limit(command))
        print(query) 
        handle.execute(query)
        return handle.fetchall()
    else: 
        query = ("SELECT SpecificBeanBarName, Company, Countries.EnglishName as company_location, Rating, CocoaPercent, sourceloc.EnglishName as source_location " 
             + "FROM BARS JOIN Countries sourceloc ON Bars.BroadBeanOriginId= sourceloc.Id JOIN Countries ON Bars.CompanyLocationId= Countries.Id "
             + area_limit(command) + sorting(command) + sort_top(command) + limit(command))
        print(query)
        handle.execute(query)
        return handle.fetchall()

def companies(command): 
    '''
    uses other functions to parse user input into an sql query 
    sends the sql query and returns the results 
    works only for queries about companies
    
    Parameters
    ----------
    command: string
        The user-entered command for sql access 

    Returns
    -------
    tuple
        sql query results 
    '''
    query = ("SELECT Company, COUNTRIES.EnglishName, " + aggregators(command)  
        + " FROM Bars JOIN Countries  " 
        +  sell_or_source(command) + area_limit(command) 
        + " GROUP BY Company, Countries.EnglishName HAVING COUNT(*)>4" 
        + " ORDER BY " +  aggregators(command) + sort_top(command) 
        + limit(command))
    print(query) 
    handle.execute(query)
    return handle.fetchall()

def countries(command): 
    '''
    uses other functions to parse user input into an sql query 
    sends the sql query and returns the results 
    works only for queries about countries 
    
    Parameters
    ----------
    command: string
        The user-entered command for sql access 

    Returns
    -------
    tuple
        sql query results 
    '''
    query = ("SELECT COUNTRIES.EnglishName, COUNTRIES.Region, " 
            + aggregators(command)
            + "FROM Bars JOIN COUNTRIES " + sell_or_source(command)
            + area_limit(command)
            + " GROUP BY COUNTRIES.EnglishName HAVING COUNT(*)>4" 
            + " ORDER BY " +  aggregators(command) + sort_top(command) 
            + limit(command))
    print(query)
    handle.execute(query)
    return handle.fetchall()

def regions(command): 
    '''
    uses other functions to parse user input into an sql query 
    sends the sql query and returns the results 
    works only for queries about regions  
    
    Parameters
    ----------
    command: string
        The user-entered command for sql access 

    Returns
    -------
    tuple
        sql query results 
    '''
    query = ("SELECT COUNTRIES.Region, " 
            + aggregators(command)
            + "FROM Bars JOIN COUNTRIES " + sell_or_source(command)
            + " GROUP BY Region HAVING COUNT(*)>4" 
            + " ORDER BY " +  aggregators(command) + sort_top(command) 
            + limit(command))
    print(query)
    handle.execute(query)
    return handle.fetchall()

def process_command(command):
    '''
    uses other functions to return sql results 
    regardless of the type of query  
    
    Parameters
    ----------
    command: string
        The user-entered command for sql access 

    Returns
    -------
    tuple
        sql query results 
    '''
    if command.split()[0] == "bars": 
        return bars(command)
    if command.split()[0] == "companies":
        return companies(command)
    if command.split()[0] == "countries":
        return countries(command)
    if command.split()[0] == "regions":
        return regions(command)
    else: 
        print("\n We are assuming you are interested in bars \n")
        return bars(command)

def load_help_text():
    '''
    loads help text 
    
    Parameters
    ----------
    NONE

    Returns
    -------
    string
    '''
    with open('Proj3Help.txt') as f:
        return f.read()

# Part 2 & 3: Implement interactive prompt and plotting. We've started for you!

def print_results(sql_tuples):
    '''
    formats sql outputs and prints out in a tableish format
    
    Parameters
    ----------
    sql_tuples: tuples
        sql results 

    Returns
    -------
    NONE
        prints formatted output 
    '''
     #This truncates everything at 12 
    new_list = []
    for observation in sql_tuples: 
        new_inner_list = []
        for thing in observation: 
            str_thing = str(thing)
            if len(str_thing) > 12: 
                new_inner_list.append(str_thing[0:12] + "...")
            else: 
                new_inner_list.append(str_thing[0:12])
        new_list.append(new_inner_list)
        
    #use the tabulate function to print out prettily 
    print("")
    print(tabulate(new_list, tablefmt = "plain", floatfmt=".1f"))
    print("")

def graph_results(sql_tuples, command): 
    '''
    displays a bar chart of the sql results 
    
    Parameters
    ----------
    command: string
        The user-entered command for sql access 
    sql_tuples: tuple 
        the sql results 

    Returns
    -------
    None
        displays a bar chart of the results 
    '''

    xvals = []

    for observation in sql_tuples: 
        xvals.append(observation[0])

    yvals = []

    if command.split()[0] == "bars" and command.find("cocoa") != -1: 
        for observation in sql_tuples: 
            yvals.append(observation[4])

    elif command.split()[0] != "countries" and command.split()[0] != "companies" and command.split()[0] != "regions": 
        for observation in sql_tuples: 
            yvals.append(observation[3])
    
    else: 
        for observation in sql_tuples: 
            yvals.append(observation[len(observation)-1])

    bar_data = go.Bar(x=xvals, y=yvals)
    basic_layout = go.Layout(title="Your requested chart")
    fig = go.Figure(data=bar_data, layout=basic_layout)
    fig.show()

def interactive_prompt():
    '''
    Prompts user for a command, checks input, returns sql results in a table or a chart 

    Parameters
    ----------
    None

    Returns
    -------
    None
    '''
    help_text = load_help_text()
    response = ""
    while response != 'exit':
        response = input('Enter a command: ')

        if response == 'exit':
            break

        if response == 'help':
            print(help_text)
            continue
        
        #ensures the response is a number or a key word 
        allowable_words = ["barplot", "top", "bottom", "regions", "countries", "companies", "bars",
                          "cocoa", "sell", "source", "number_of_bars", "rating", "ratings" ]
        
        bad_response =0 
        for word in response.split():
            if word not in  allowable_words and word.isdigit() == False and word.find("region=") == -1 and word.find("subregion=") == -1 and word.find("country=") == -1:
            #any(word NOT in response for word in allowable_words): 
                print("Your reponse includes an unreadable word: " + word + "\n")
                bad_response = 1
        if bad_response == 1: continue 
         
        if response.find("barplot") != -1: 
            try:
                output = process_command(response)
                if output == []:
                    print("\n One of your specifications does not exist in the database.\n")
                else: graph_results(output,response)
            except: 
                print("Not all options work with all queries")

        else: 
            try:
                output = process_command(response)
                if output == []:
                    print("\n One of your specifications does not exist in the database.\n")
                else: print_results(output)
            except: 
                print("Not all options work with all queries")
    
#interactive_prompt()
# Make sure nothing runs or prints out when this file is run as a module/library
if __name__=="__main__":
    interactive_prompt()
