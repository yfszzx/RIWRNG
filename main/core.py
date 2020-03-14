import rdrand as rd
RAND_NUMBER_NUM = 4000
def _get_rand_num():
    rnd = 0
    rnd_rsc = []
    for i in range(RAND_NUMBER_NUM):
        num = rd.rdrand_get_bits(2) 
        rnd += num % 2
        rnd_rsc += int((num - rnd) / 2)
    return rnd, rnd_rsc

def _core(usr, mod):
    rnd, rnd_rsc = _get_rand_num()
    experiment.objects.create(
        user=usr,
        rnd_num=RAND_NUMBER_NUM,
        exp_mod=mod,
        exp_score=rnd,
        research_score=rnd_rsc
        )
    scr = score.objects.get(user=usr)
    if mod == 't':
        scr.train_score += rnd
        scr.train_num += RAND_NUMBER_NUM
    elif mod == 'e':
        scr.exp_score += rnd
        scr.exp_num += RAND_NUMBER_NUM
    elif mod == 'v':
        scr.verify_score += rnd
        scr.verify_num += RAND_NUMBER_NUM
    scr.save()
    return rnd