import os
import random
import re
import sys
import copy

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:  
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.
    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    model = {}
    nbOfPages = len(corpus[page])
    #if the page does contain any links, pretend that it has a link to every page inculding it self
    if nbOfPages == 0:
        nbOfPages = len(corpus)
        for nextPage in corpus:
            model[nextPage] = 1/len(corpus)
    else:
        model[page] = round((1-damping_factor)/ (nbOfPages +1), 4) # +1 for the current page
        for nextPage in corpus[page]:
            model[nextPage] = round((1-damping_factor)/ (nbOfPages + 1) + damping_factor * 1/nbOfPages, 4)
    
    return model


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    #init ranks of pages to 0
    ranks = {}
    for page in corpus:
        ranks[page] = 0
    
    #get random page from corpus and get it's transion model
    nbOfPages = len(corpus)
    randomIndex = random.randrange(nbOfPages)
    currentPage = list(ranks.keys())[randomIndex]

    ranks[currentPage] += 1

    for i in range(n-1):
        currentModel = transition_model(corpus, currentPage, damping_factor)

        #select a random page from the current model if in range of damping factor
        #otherwise choose a page randomly from the corpus
        randomNb = random.random()
        if(randomNb >= 1-damping_factor): #if damping factor is 0.85 then a randomNb of 0.15 to 1 will satisfy the condition
            randomNb = random.random()
            sum = 0
            for page in currentModel:
                sum += currentModel[page]
                if(randomNb <= sum):
                    currentPage = page
                    break
        else:
            randomIndex = random.randrange(nbOfPages)
            currentPage = list(ranks.keys())[randomIndex]

        #update rank of the selected page
        ranks[currentPage] += 1
        
    #update ranks so that it sums up to 1
    for page in ranks:
        ranks[page] /= SAMPLES

    return ranks
        

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
                
    #init page ranks
    ranks = {}
    nbOfPages = len(corpus)
    for page in corpus:
        ranks[page] = 1/nbOfPages

    #check for pages not having any links and if there is, pretend that it has a link to every page inculding it self
    for pageToCheck in corpus:
        if(len(corpus[pageToCheck]) == 0):
            allPages = set(corpus.keys())
            corpus[pageToCheck] = allPages
            
    
    #calc page ranks until every page rank difference is less than 0.001
    while(True):
        prevRanks = copy.deepcopy(ranks)
        for page in ranks:
            ranks[page] = calcPageRank(page,corpus,ranks, damping_factor)

        #check ranks difference, if there is rank with not the desired difference then loop calculate ranks again
        flag = True
        for page in ranks:
            if(abs(prevRanks[page] - ranks[page]) > 0.001):
                flag = False
                break
        if(flag == True):
            break

    return ranks
 
       
#page rank = (1-damping)/number of pages + 
# damping * sumof(rank of a page that link to the currpage/ number of links in the page that link to the currpage)
def calcPageRank(pageToCalculate, corpus, ranks, damping_factor):
    sumOfRightSide = 0
    #look for pages that link to the pageToCalculate 
    for page in corpus:
        if pageToCalculate in corpus[page]:
            sumOfRightSide += round(ranks[page]/len(corpus[page]), 4)
    rank = round((1-damping_factor)/len(corpus), 4) + round(damping_factor * sumOfRightSide, 4)

    return rank


if __name__ == "__main__":
    main()
