import requests
from bs4 import BeautifulSoup
import os
import re
import time
import ML
from pathlib import Path

    
# Iterates over all the matches of given user0
# and geneates .mat file for each game

def main(user0, maxFiles, OUTPUT_DIR):

    # ==== USER CONFIGURATION ====

    MYUSERNAME = "OLLIDan"
    MYPASSWORD = "plum"   # plain password, not the cookie value
    
    
    # DG codes assigned to each user
    userCodeOf = {"OLLIDan"           : 42169,
                  "OLLIAlan"          : 40145,
                  "EdM"               : 42242,
                  "igaRugga"          : 39653,
                  "kaori"             : 40997,
                  "kathyv"            : 42213,
                  "Lil Maus"          : 38555,
                  "OLLI CCYHI"        : 41606,
                  "OLLI Jane"         : 39590,
                  "OLLI marco"        : 39597,
                  "OLLI TerAlligator" : 39150,
                  "OLLIboba"          : 39423,
                  "OLLIrada"          : 40399,
                  "ollisydni"         : 42402,
                  "ANESTIS"           : 33114,
                  "Top Notch"         : 18660,
                  "DichiBerlin"       : 22426,
                  "Willie Wonka"      : 4872
                  }
    
    
    # ==== URLs ====
    
    # They are obtained by going to my browser, logging into DG,
    # and getting the URSs
    
    dg_url    = "http://dailygammon.com"           # DG does not support https
    base_url  = f"{dg_url}/bg"
    home_url  = f"{base_url}/index.html"
    login_url = f"{base_url}/login"
    user_url  = f"{base_url}/user"
    
    # ==== START A SESSION  =========
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Referer": home_url
    })
    
    # ==== LOGIN  =========
    
    data = {
        "login"   : MYUSERNAME,
        "password": MYPASSWORD,
    }
    
    # Use Mozilla to log in into DG
    # r.text is the html of the welcome page
    r = session.post(login_url, data=data, timeout=30)
    
    if "Logout" not in r.text and "logout" not in r.text:
        ML.trace(0, "Login failed -- check username/password.")
        ML.trace(0, r.text[:400])
        raise SystemExit
    
    ML.trace(10, "Logged in successfully")
    
    
    # ==== USER0's PAGE OF ALL MATCHES  =========
    
    
    # session.get() returns r.text containing the html of the page listing all matches
    r = session.get(f"{user_url}/{userCodeOf[user0]}?sort_event=1&finished=1",
                    timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    
    
    # ==== USER0's PAGE OF ALL MATCHES  =========
    
    # a iterates over the strings of the form <A href=/bg/game/5170614/1/list>
    # a["href"] is /bg/game/5170614/1/list
    # but we limit ourselfs to those of the form /bg/export/5170614
    match_links = [
        a["href"]
        for a in soup.find_all("a", href=True)
        if "/bg/export/" in a["href"]
    ]
    
    if not match_links:
        ML.trace(10, "No matches found on user page.")
    else:
        ML.trace(10, f"Found {len(match_links)} matches.")
        
        
        # ==== DOWNLOAD  =========
        
        userOutputDir = f"{OUTPUT_DIR}\{user0}"
        os.makedirs(userOutputDir, exist_ok=True)             # Create the output directory
        
        for i, link in enumerate(match_links, start=1):
            if i > maxFiles:
                break                                      # already considered all the files for download
    
            match_id = re.search(r"/export/(\d+)", link)   # extract 5170613 into match_id.group(1)
            if not match_id:
                continue                                   # not something that can be exported
            
            outputFileName = match_id.group(1)+".mat"      # 5170613.mat
            fullFileName = os.path.join(userOutputDir, outputFileName)

            if Path(fullFileName).is_file():
                continue                                   # already there

            # get the contents of 5170613
            r = session.get(f"{dg_url}{link}?export=mat",
                            timeout=30)
            
            # Check if it describes a match
            if not (r.ok and b"Wins" in r.content):              
                continue
                
            
            with open(fullFileName, "wb") as f:
                f.write(r.content)
                ML.trace(10, f"Downloading match {i}/{len(match_links)}: {outputFileName} ...")
        
        
            # ==== EPILOG  =========
            
            time.sleep(1)  # delay to look like a human, not DOS attack

    
    ML.trace(10, "All done.")


if __name__ == "__main__":
    
    # ==== ARGUMENTS ====

    user0      = ML.getArg(1, "OLLIDan" ) 
    maxFiles   = ML.getArg(2, 1234567890)     # maximum number of files to extract
    OUTPUT_DIR = ML.getArg(3, "matches")
    
    main(user0, maxFiles, OUTPUT_DIR)
