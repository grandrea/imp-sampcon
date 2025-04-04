"""@namespace IMP.sampcon.clustering_rmsd
   Utilities to cluster and calculate RMSD and precision"""

import numpy
import math
import scipy.stats
from multiprocessing import Pool


def get_sample_identity(idfile_A, idfile_B):
    # whether a run belongs to run1 or run2
    sampleA_models = []
    sampleB_models = []

    with open(idfile_A, 'r') as f:
        for line in f:
            mod = line.split("/")[-1]
            sampleA_models.append(int(mod.strip("\n").split(" ")[1]))
    f.close()

    with open(idfile_B, 'r') as f:
        for line in f:
            mod = line.split("/")[-1]
            sampleB_models.append(int(mod.strip("\n").split(" ")[1]))
    return sampleA_models, sampleB_models


def get_cutoffs_list(distmat, gridSize):

    mindist = distmat.min()
    maxdist = distmat.max()

    print("Minimum and maximum pairwise model distances:", mindist, maxdist)
    cutoffs = numpy.arange(mindist+gridSize, maxdist, gridSize)
    return cutoffs


def precision_cluster(distmat, numModels, rmsd_cutoff):
    # STEP 2. Populate the neighbors ofa given model
    neighbors = []
    for count in range(numModels):
        neighbors.append([count])  # model is a neighbor of itself

    # set of i,j indices that pass
    inds = numpy.argwhere(distmat <= rmsd_cutoff)
    for x in inds:
        i = x[0]
        j = x[1]
        # Only count each contribution once
        if i > j:
            neighbors[i].append(j)
            neighbors[j].append(i)

    # STEP 3. Get the weightiest cluster, and iterate
    unclustered = []
    boolUnclustered = []
    for i in range(numModels):
        unclustered.append(i)
        boolUnclustered.append(True)

    cluster_members = []   # list of lists : one list per cluster
    cluster_centers = []

    while len(unclustered) > 0:
        # get cluster with maximum weight
        max_neighbors = 0
        currcenter = -1
        for eachu in unclustered:
            # if multiple clusters have same maxweight this tie is
            # broken arbitrarily!
            if len(neighbors[eachu]) > max_neighbors:
                max_neighbors = len(neighbors[eachu])
                currcenter = eachu

        # form a new cluster with u and its neighbors
        cluster_centers.append(currcenter)
        cluster_members.append([n for n in neighbors[currcenter]])

        # update neighbors
        for n in neighbors[currcenter]:
            # removes the neighbor from the pool
            unclustered.remove(n)  # first occurrence of n is removed.
            boolUnclustered[n] = False  # clustered

        for n in neighbors[currcenter]:
            for unn in neighbors[n]:  # unclustered neighbor
                if not boolUnclustered[unn]:
                    continue
                neighbors[unn].remove(n)

    return cluster_centers, cluster_members


def get_contingency_table(num_clusters, cluster_members, all_models,
                          run1_models, run2_models):
    full_ctable = numpy.zeros((num_clusters, 2))

    for ic, cluster in enumerate(cluster_members):
        for member in cluster:
            model_index = all_models[member]

            if model_index in run1_models:
                # print("run1", model_index)
                full_ctable[ic][0] += 1.0
            elif model_index in run2_models:
                # print("run2", model_index)
                full_ctable[ic][1] += 1.0

    # now normalize by number of models in each run
    reduced_ctable = []
    retained_clusters = []

    for i in range(num_clusters):
        if full_ctable[i][0] <= 10.0 or full_ctable[i][1] <= 10.0:
            continue
        reduced_ctable.append([full_ctable[i][0], full_ctable[i][1]])
        retained_clusters.append(i)
    return numpy.array(reduced_ctable), retained_clusters


def test_sampling_convergence(contingency_table, total_num_models):
    if len(contingency_table) == 0:
        return 0.0, 1.0

    ct = numpy.transpose(contingency_table)
    [chisquare, pvalue, dof, expected] = scipy.stats.chi2_contingency(ct)
    if dof == 0.0:
        cramersv = 0.0
    else:
        cramersv = math.sqrt(chisquare/float(total_num_models))

    return pvalue, cramersv


def percent_ensemble_explained(ctable, total_num_models):
    if len(ctable) == 0:
        return 0.0
    percent_clustered = \
        float(numpy.sum(ctable, axis=0)[0] + numpy.sum(ctable, axis=0)[1]) \
        * 100.0 / float(total_num_models)
    return percent_clustered


def unpacking_wrapper(arg_tuple):
    x = arg_tuple[2:]
    all_models, run1_all_models, run2_all_models, total_num_models = x
    x = precision_cluster(*((distmat_full, ) + arg_tuple[0:2]))
    cluster_centers, cluster_members = x
    ctable, retained_clusters = get_contingency_table(
        len(cluster_centers), cluster_members, all_models,
        run1_all_models, run2_all_models)
    pval, cramersv = test_sampling_convergence(ctable,
                                               total_num_models)
    percent_explained = percent_ensemble_explained(ctable,
                                                   total_num_models)
    return pval, cramersv, percent_explained


def init_foo(distmat):
    global distmat_full
    distmat_full = distmat


def get_clusters(cutoffs_list, distmat_full, all_models, total_num_models,
                 run1_all_models, run2_all_models, sysname, cores):
    # Do Clustering on a Grid
    pvals = []
    cvs = []
    percents = []
    with open("%s.ChiSquare_Grid_Stats.txt" % sysname, 'w+') as f1:
        p = Pool(cores, init_foo, initargs=(distmat_full, ))
        args_list = [(total_num_models, c, all_models, run1_all_models,
                      run2_all_models, total_num_models)
                     for c in cutoffs_list]
        results = p.map(unpacking_wrapper, args_list)
        for i, x in enumerate(results):
            pvals.append(x[0])
            cvs.append(x[1])
            percents.append(x[2])

            print(cutoffs_list[i], x[0], x[1], x[2], file=f1)

    return pvals, cvs, percents


def get_sampling_precision(cutoffs_list, pvals, cvs, percents):
    sampling_precision = max(cutoffs_list)
    pval_converged = 0.0
    cramersv_converged = 1.0
    percent_converged = 0.0

    for i in range(len(cutoffs_list)):
        if percents[i] > 80.0:
            if pvals[i] > 0.05 or cvs[i] < 0.10:
                if sampling_precision > cutoffs_list[i]:
                    sampling_precision = cutoffs_list[i]
                    pval_converged = pvals[i]
                    cramersv_converged = cvs[i]
                    percent_converged = percents[i]
        else:
            sampling_precision = max(cutoffs_list)

    return (sampling_precision, pval_converged, cramersv_converged,
            percent_converged)
