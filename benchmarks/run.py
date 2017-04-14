if __name__ == "__main__":

    from perf import run as run_perf
    from prof import run as run_profile

    results1 = run_perf()
    results2 = run_perf()
    results3 = run_perf()

    many_avg = (results1[0].elapsed + results2[0].elapsed + results3[0].elapsed) / 3
    one_avg = (results1[1].elapsed + results2[1].elapsed + results3[1].elapsed) / 3

    print('Serializing many took {elapsed} seconds(avg)'.format(
        elapsed=many_avg
    ))
    print('Serializing one took {elapsed} seconds(avg)'.format(
        elapsed=one_avg
    ))
