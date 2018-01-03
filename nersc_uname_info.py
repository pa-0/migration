#
# provides name, email, and affiliation for nersc unames
# that were used to develop visit
#

import sys
import json

# from svn_utils.svn_list_authors()
def svn_authors():
    return [
      "alexanda", 
      "miller86", 
      "selby", 
      "sveta", 
      "mblair", 
      "rbleile", 
      "jimeliot", 
      "fogal1", 
      "alister", 
      "cyrush", 
      "ahern", 
      "pascal", 
      "mlarsen", 
      "loring", 
      "semeraro", 
      "js9", 
      "sisneros", 
      "allens", 
      "brownlee", 
      "pnav", 
      "oruebel", 
      "whitlocb", 
      "hrchilds", 
      "rhudson", 
      "shelly", 
      "sidshank", 
      "kbensema", 
      "hota", 
      "garth", 
      "maheswar", 
      "dskinner", 
      "bonnell", 
      "tarwater", 
      "cary", 
      "prabhat", 
      "kgriffin", 
      "wheeler", 
      "laney", 
      "cook47", 
      "deines", 
      "ghweber", 
      "hkrishna", 
      "iulian", 
      "gmorris2", 
      "treadway", 
      "brugger", 
      "kdawes", 
      "dbremer", 
      "iuri", 
      "knolla", 
      "eewing", 
      "camp", 
      "jcanders", 
      "pugmire", 
      "apletzer", 
      "spetruzz", 
      "mdurant", 
      "camc", 
      "stratton"
    ]

# details pulled from:  src/svn_bin/nersc_username_to_email
def uname_info():
    r = {
    "ahren":  {"name" : "Sean Ahern",
               "afil" : "Oak Ridge National Laboratory",
               "email": "ahern@ornl.gov"},
    #
    "js9":  {"name" : "Jeremy Meredith",
             "afil" : "Oak Ridge National Laboratory",
             "email": "jsmeredith@gmail.com"},
    #
    "hrchilds":  {"name" : "Hank Childs",
                  "afil" : "University of Oregon",
                  "email": "hank@uoregon.edu"},
    #
    "miller86":  {"name" : "Mark Miller",
                  "afil" : "Lawrence Livermore National Laboratory",
                  "email": "miller86@llnl.gov"},
    #
    "whitlocb":  {"name" : "Brad Whitlock",
                  "afil" : "Intelligent Light",
                  "email": "bjw@ilight.com"},
    #
    "cyrush":  {"name" : "Cyrus Harrison",
                "afil" : "Lawrence Livermore National Laboratory",
                "email": "cyrush@llnl.gov"},
    #
    "dbremer":  {"name" : "David Bremer",
                 "afil" : "Lawrence Livermore National Laboratory",
                 "email": "bremer4@llnl.gov"},
    #
    "ghweber":  {"name" : "Gunther Weber",
                 "afil" : "Lawrence Berkeley National Laboratory",
                 "email": "ghweber@lbl.gov"},
    #
    "bonnell":  {"name" : "Kathleen Bonnell",
                 "afil" : "Lawrence Livermore National Laboratory",
                 "email": "bonnell2@llnl.gov"},
    #
    "brugger":  {"name" : "Eric Brugger",
                 "afil" : "Lawrence Livermore National Laboratory",
                 "email": "brugger1@llnl.gov"},
    #
    "kgriffin":  {"name" : "Kevin Griffin",
                  "afil" : "Lawrence Livermore National Laboratory",
                  "email": "griffin28@llnl.gov"},
    #
    "fogal1":  {"name" : "Tom Fogal",
                "afil" : "SCI Institute, University of Utah",
                "email": "tfogal@sci.utah.edu"},

    #
    "pugmire":  {"name" : "Dave Pugmire",
                 "afil" : "Oak Ridge National Laboratory",
                 "email": "pugmire@ornl.gov"},

    #
    "stratton":  {"name" : "Josh Stratton",
                  "afil" :"SCI Institute, University of Utah",
                  "email": "strattonbrazil@gmail.com"},

    #
    "rhudson":  {"name" : "Randy Hudson",
                 "afil" : "University of Chicago, Argonne National Laboratory",
                 "email": "hudson@mcs.anl.gov"},
    #
    "camp":  {"name" : "David Camp",
              "afil" : "Lawrence Berkeley National Laboratory",
              "email": "dcamp@lbl.gov"},
    #
    "semeraro":  {"name" : "Dave Semeraro",
                  "afil" : "NCSA, University of Illinois",
                  "email": "semeraro@ncsa.uiuc.edu"},
    #
    "pnav":  {"name" : "Paul Navratil",
              "afil" :"TACC, University of Texas",
              "email": "pnav@tacc.utexas.edu"},
    #
    "mdurant":  {"name" : "Marc Durant",
                 "afil" :"Tech-X Corp",
                 "email": "mdurant@txcorp.com"},
    #
    "hkrishna":  {"name" : "Harinarayan(Hari) Krishnan",
                  "afil" : "Lawrence Berkeley National Laboratory",
                  "email": "hkrishnan@lbl.gov"},
    #
    "cook47":  {"name" : "Rich Cook",
                 "afil" : "Lawrence Livermore National Laboratory",
                 "email": "rcook@llnl.gov"},
    #
    "loring":  {"name" : "Burlen Loring",
                 "afil" : "Lawrence Berkeley National Laboratory",
                 "email": "bloring@lbl.gov"},
    #
    "allens":  {"name" : " Allen Sanderson",
                "afil" : "SCI Institute, University of Utah",
                "email": "allen@sci.utah.edu"},
    #
    "oruebel":  {"name" : "Oliver Ruebel",
                 "afil" : "Lawrence Berkeley National Laboratory",
                 "email": "allen@sci.utah.edu"},
    #
    "iuri":  {"name" : "Iuri Prilepov",
              "afil" : "UC Davis & Lawrence Berkeley National Laboratory",
              "email": "iprilepov@lbl.gov"},
    #
    "wheeler":  {"name" : "Matthew Wheeler",
                 "afil" : "AWE UK",
                 "email": "Matthew.Wheeler@awe.co.uk"},
    #
    "maheswar":  {"name" : "Satheesh Maheswaran",
                  "afil" : "AWE UK",
                  "email": "Satheesh.Maheswaran@awe.co.uk"},
    #
    "selby":  {"name" : "Paul Selby",
               "afil" : "AWE UK",
               "email": "paul.selby@awe.co.uk"},
    #
    "kbensema":  {"name" : "Kevin Bensema",
                  "afil" : "UC Davis",
                  "email": "kbensema@ucdavis.edu"},
    #
    "camc":  {"name" : "Cameron Christensen",
              "afil" : "SCI Institute, University of Utah",
              "email": "cam@sci.utah.edu"},
    #
    "rbleile":  {"name" : "Ryan Bleile",
                 "afil" : "University of Oregon",
                 "email": "rbleile@cs.uoregon.edu"},
    #
    "jimeliot":  {"name" : "Jim Eliot",
                  "afil" : "AWE UK",
                  "email": "jim.eliot@awe.co.uk"},
    #
    "iulian":  {"name" : "Iulian Grindeanu",
                "afil" : "Argonne National Laboratory",
                "email": "iulian@anl.gov"},
    #
    "gmorriso":  {"name" : "Garrett Morrison",
                  "afil" : "University of Oregon",
                  "email": "gmorriso@uoregon.edu"},
    #
    "alister":  {"name" : "Alister Maguire",
                 "afil" : "Lawrence Livermore National Laboratory",
                 "email": "maguire7@llnl.gov"}
    }
    return r


def uncovered_authors():
    res = []
    umap = uname_info()
    for author in svn_authors():
        if not author in umap.keys():
            res.append(author)
    return res

ua = uncovered_authors()
if len(ua) > 0:
    print "warning: uncovered authors:"
    print json.dumps(ua,indent=2)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print json.dumps(uname_info()[sys.argv[1]],indent=2)
    else:
        print json.dumps(uname_info(),indent=2)

