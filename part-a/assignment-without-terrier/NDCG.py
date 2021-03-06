#!/usr/bin/python

########################################################################################################################

# Ref: https://en.wikipedia.org/wiki/Discounted_cumulative_gain#Normalized_DCG

########################################################################################################################


# python packages
from math import log2
from collections import OrderedDict


########################################################################################################################


# loads results
def load_results(input_file):

    # list to hold data
    qid_did = []
    # list to hold query ids
    query_ids = []

    # open file
    with open(input_file) as input_file:
        # for every line in input file
        for line in input_file:
            # split line into tokens
            tokens = line.strip(' \n').split(' ')
            # assign first token to query id
            query_id = tokens[0]
            # if query id is not in query ids list
            if query_id not in query_ids:
                # add query id to query ids list
                query_ids += [query_id]
            # convert to int and assign fourth token to document rank
            doc_rank = int(tokens[3])
            # if document rank is less than 50
            if doc_rank < 50:
                # assign third token to document id
                doc_id = tokens[2]
                # concatenate query id and document id and assign to query id document id
                qid_did_temp = ' '.join([query_id, doc_id])
                # add temporary query id document id to query id document id list
                qid_did += [qid_did_temp]

    # return query id document id and query ids lists
    return qid_did, query_ids


########################################################################################################################


# loads qrels
def load_qrels(input_file):

    # dictionary to hold document relevance
    doc_rel = OrderedDict({})

    # open file
    with open(input_file) as input_file:
        # for every line in input file
        for line in input_file:
            # split line into tokens
            tokens = line.strip(' \n').split(' ')
            # assign first token to query id
            query_id = tokens[0]
            # assign third token to document id
            doc_id = tokens[2]
            # assign fourth token to temporary document relevance
            doc_rel_temp = int(tokens[3])
            # concatenate query id and document id and assign to query id document id
            qid_did = ' '.join([query_id, doc_id])
            # add temporary document relevance to document relevance dictionary
            doc_rel[qid_did] = doc_rel_temp

    # return doc relevance
    return doc_rel


########################################################################################################################


# calculates ndcg
def calc_ndcg(results, doc_rel, k, start, end):

    # get document relevance scores for document ids between start and end
    rels = [doc_rel.get(results[i]) if doc_rel.get(results[i]) is not None else 0 for i in range(start, end)]

    # if relevance score is greater than or equal to 1, rescale to 1, else 0 (binary)
    rels = [1 if x >= 1 else 0 for x in rels]

    # sort relevance scores in descending order and assign to sorted relevance scores
    sorted_rels = sorted(rels, reverse=True)

    # assign first relevance score to relevance score 1
    rel1 = rels[0]
    # assign first sorted relevance score to sorted relevance score 1
    sorted_rel1 = sorted_rels[0]

    # calculate dcg fraction
    # method 1 - wikipedia
    dcg_fraction = sum([(rels[i] / log2(i)) for i in range(2, k)])
    # method 2 - microsoft research paper
    # dcg_fraction = sum([(rels[i] / log2(i + 1)) for i in range(1, k)])
    # calculate idcg fraction
    # method 1 - wikipedia
    idcg_fraction = sum([(sorted_rels[i] / log2(i)) for i in range(2, k)])
    # method 2 - microsoft research paper
    # idcg_fraction = sum([(sorted_rels[i] / log2(i + 1)) for i in range(1, k)])

    # calculate dcg
    dcg = rel1 + dcg_fraction
    # calculate idcg
    idcg = sorted_rel1 + idcg_fraction

    # set ndcg to 0.0
    ndcg = 0.0

    # if dcg and idcg are not equal to 0 or 0.0
    if dcg and idcg != 0 or 0.0:
        # calculate ndcg
        ndcg = dcg / idcg

    # return ndcg
    return ndcg


########################################################################################################################


# main function
def main():

    # load results
    results, query_ids = load_results('input/BM25b0.75_0.res')
    # load qrels
    doc_rel = load_qrels('input/qrels.adhoc.txt')

    # assign length of query ids to query ids length
    query_ids_len = len(query_ids)
    # list to hold ndcg at k in (1, 5, 10, 20, 30, 40, 50)
    all_ndcg = [0.0 for _ in range(7)]

    # for every query id
    for query_id in query_ids:
        # convert query id to int and assign to query id
        query_id = int(query_id)
        # convert first query id to int and assign to query id 1
        query_id1 = int(query_ids[0])

        # loop from 0 to 1, 5, 10, 20, 30, 40, 50
        for k in (1, 5, 10, 20, 30, 40, 50):
            # set i to 0
            i = 0
            # if k equals 1, i equals 0
            if k == 1:
                i = 0
            # else if k equals 5, i equals 1
            elif k == 5:
                i = 1
            # else if k equals 10, i equals 2
            elif k == 10:
                i = 2
            # else if k equals 20, i equals 3
            elif k == 20:
                i = 3
            # else if k equals 30, i equals 4
            elif k == 30:
                i = 4
            # else if k equals 40, i equals 5
            elif k == 40:
                i = 5
            # else if k equals 50, i equals 6
            elif k == 50:
                i = 6

            """
                query ids 219 and 241 are missing from the results
                file provided which affects the incremental progress
                through the results.

                for example:

                query_id = 218, k = 5
                start = 50 * (218 - 201) = 50 * 17 = 850
                end = start + k = 850 + 5 = 855
                loop: from 850 to 855

                this works for query ids less than 219.

                #######################################################

                query_id = 220, k = 5
                start = 50 * (220 - 201) = 50 * 19 = 950
                end = start + k = 950 + 5 = 955
                loop: from 950 to 955

                it doesn't work anymore for query ids over 219,
                as we are not considering 50 documents, from 900
                to 950 in this case.

                #######################################################

                to fix it, we do the following:

                query_id = 220, k = 5
                start = 50 * (220 - 201 - 1) = 50 * 18 = 900
                end = start + k = 900 + 5 = 905
                loop: from 900 to 905

                #######################################################

                we also fix 241 in a similar way, except we minus by
                2 instead of 1:

                query_id = 240, k = 5
                start = 50 * (240 - 201 - 1) = 50 * 38 = 1900
                end = start + k = 1900 + 5 = 1905
                loop: from 1900 to 1905

                this works for query ids greater than 219 and less
                than 241.

                #######################################################

                query_id = 242, k = 5
                start = 50 * (242 - 201 - 1) = 50 * 40 = 2000
                end = start + k = 2000 + 5 = 2005
                loop: from 2000 to 2005

                it doesn't work anymore for query ids over 241,
                as we are not considering 50 documents, from 1950
                to 2000 in this case.

                #######################################################

                to fix it, we do the following:

                query_id = 242, k = 5
                start = 50 * (242 - 201 - 2) = 50 * 39 = 1950
                end = start + k = 1950 + 5 = 1955
                loop: from 1950 to 1955
            """
            if query_id < 219:
                start = 50 * (query_id - query_id1)
            elif 219 < query_id < 241:
                start = 50 * (query_id - query_id1 - 1)
            else:
                start = 50 * (query_id - query_id1 - 2)
            end = start + k

            # calculate ndcg and return output in ndcg
            ndcg = calc_ndcg(results, doc_rel, k, start, end)
            # add ndcg to average ndcg
            all_ndcg[i] += ndcg

    # calculate average ndcg @ k = 1
    avg_ndcg_k1 = all_ndcg[0] / query_ids_len
    # calculate average ndcg @ k = 5
    avg_ndcg_k5 = all_ndcg[1] / query_ids_len
    # calculate average ndcg @ k = 10
    avg_ndcg_k10 = all_ndcg[2] / query_ids_len
    # calculate average ndcg @ k = 20
    avg_ndcg_k20 = all_ndcg[3] / query_ids_len
    # calculate average ndcg @ k = 30
    avg_ndcg_k30 = all_ndcg[4] / query_ids_len
    # calculate average ndcg @ k = 40
    avg_ndcg_k40 = all_ndcg[5] / query_ids_len
    # calculate average ndcg @ k = 50
    avg_ndcg_k50 = all_ndcg[6] / query_ids_len

    # write ndcg @ k in (1, 5, 10, 20, 30, 40, 50) to file
    with open('output/temp/bm25_ndcg.txt', mode='w') as results_file:
        results_file.write('bm25\n')
        results_file.write('K\t|\tNDCG@K\n')
        results_file.write('1\t|\t{0:.3f}\n'.format(avg_ndcg_k1))
        results_file.write('5\t|\t{0:.3f}\n'.format(avg_ndcg_k5))
        results_file.write('10\t|\t{0:.3f}\n'.format(avg_ndcg_k10))
        results_file.write('20\t|\t{0:.3f}\n'.format(avg_ndcg_k20))
        results_file.write('30\t|\t{0:.3f}\n'.format(avg_ndcg_k30))
        results_file.write('40\t|\t{0:.3f}\n'.format(avg_ndcg_k40))
        results_file.write('50\t|\t{0:.3f}'.format(avg_ndcg_k50))
    # print progress
    print('\nSaved results to file at path: \'{}\'\n'.format(results_file.name))


########################################################################################################################


# runs main function
if __name__ == '__main__':
    main()


########################################################################################################################
