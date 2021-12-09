from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import requests as rq
import json
from django.shortcuts import redirect
import json
import pandas as pd
import numpy as np
def kernal(input_dict, sex, age, professional, ele, ele_sym, sym_freq):
    def get_belong_syms(input_dict, sym_belong):
        syms = []
        while len(syms) != len(input_dict):
            new_syms = np.setdiff1d(input_dict.keys(), syms)
            syms = input_dict.keys()
            belong = np.intersect1d(new_syms,  sym_belong.keys())
            for i in belong: 
                if input_dict[i] < 1:
                    continue
                for k in sym_belong[i]:
                    if k in input_dict: 
                        continue                
                    input_dict[k] = input_dict[i]
        return input_dict
    
    def remove_syms(syms_list, age, sex, professional, sym_class_dict):
        remove_class = []
        if age <= 8:
            remove_class.append(90) #妇科
            remove_class.append(1000) #男科
        if age > 8:
            remove_class.append(83) #儿科
            if sex == 0:
                remove_class.append(1000) #男科
            else:
                remove_class.append(90) #妇科
        if not professional:
            remove_class.append(26) #舌象
            remove_class.append(142) #脉象
        ret = []
        for s in syms_list:
            if s not in sym_class_dict:
                continue                
            cls = np.intersect1d(sym_class_dict[s], remove_class)
            if len(cls) > 0:
                continue
            ret.append(s)
        return ret
    sym = pd.read_pickle("database/symptom.pkl")      
    sym_class_dict = np.load("database/sym_class_dict.npy", allow_pickle=True).tolist()
    class_name = pd.read_pickle("database/class_name.pkl")    
    sym_belong = np.load("database/sym_belong.npy", allow_pickle=True).tolist()
    input_dict = get_belong_syms(input_dict, sym_belong) 
    gp = ele_sym.groupby("ele")
    res = {}
    sym_predict = []
    for e, dt in gp:
        morbidity = ele["freq"][e]
        p_positive = morbidity
        dt.index = dt["sym"].values
        idx = np.intersect1d(dt.index, list(input_dict.keys()))
        for s in idx:
            
            if input_dict[s] == 0: #不确定
                continue                
            if input_dict[s] < 0: #否认：
                positive = p_positive * (1 - dt["freq"][s])
                negative = (1 - positive) * ((1 - sym_freq[s]) - (1 - dt["freq"][s]) * morbidity)/(1 - morbidity) 
            else:
                grade = input_dict[s] / 2 # 1: 轻微 2：明显 3：严重
                positive = p_positive * dt["freq"][s] * grade
                negative = (1 - p_positive) * (sym_freq[s] - dt["freq"][s]* grade * morbidity)/(1 - morbidity) 
            p_positive = positive /(positive + negative)   
           
        res[e] = [ele["name"][e], p_positive]
        sym_predict.append(dt["freq"] * p_positive) 
   
    sym_predict = pd.concat(sym_predict, axis=1).sum(axis=1)   
    idx = np.setdiff1d(sym_predict.index, list(input_dict.keys()))
    idx = remove_syms(idx, age, sex, professional, sym_class_dict)
    sym_predict = pd.concat([sym["name"][idx], sym_predict[idx]], axis=1)
    sym_predict.columns = ["name","pred"]    
    res = pd.DataFrame(res).T
    res.columns = ["name", "prob"]
    ipt = {}
    for s in input_dict.keys():
        ipt[sym["name"][s]] = input_dict[s]
    return res.sort_values("prob", ascending=False), sym_predict.sort_values("pred", ascending=False), ipt

def element_judge(input_dict, sex, age, professional, num):
    ele = pd.read_pickle("database/element.pkl")    
    ele_sym = pd.read_pickle("database/ele_sym.pkl")
    sym_freq = pd.read_pickle("database/sym_freq_ele.pkl")
    res, sym_predict, ipt = kernal(input_dict, sex, age, professional, ele, ele_sym, sym_freq)
    res = res.iloc[:num]
    return res, sym_predict, ipt
    
def disease_judge(main_symptom, input_dict, sex, age, professional, num):
    ele = pd.read_pickle("database/disease.pkl")   
    ele.loc[945,"freq"] /= 4 # 中风
    ele.loc[830, "freq"] /= 4 #眩晕
    ele.loc[252, "freq"] /= 4 #肛瘘
#     ele.loc[250, "freq"] *= 2 #感冒
    
    ele_sym = pd.read_pickle("database/dis_sym.pkl")
    prob_dis = ele_sym["ele"][ele_sym["sym"] == main_symptom].values
    sym_freq = pd.read_pickle("database/sym_freq_dis.pkl")   
    gp = ele_sym.groupby("ele")
    concat = []
    for i , dt in gp:
        if i in prob_dis:
            dt["ele"] = i
            concat.append(dt)
    ele_sym = pd.concat(concat).reset_index(drop=True)
    res, sym_predict, ipt = kernal(input_dict, sex, age, professional, ele, ele_sym, sym_freq)
    res = res.sort_values("prob", ascending=False)
    res = res.iloc[:num]
    res["prob"] = res["prob"] * ele["freq"][res.index]
    return res, sym_predict, ipt

def get_judgement(main_sym, symptoms, sex, age, profession, disease_num, element_num):
    def pd2dict(pd, field):
        ret = {}
        for i in pd.index:
            ret[i] = [pd["name"][i], pd[field][i]]
        return ret
    ele_res, ele_sym_predict, ipt =  element_judge(symptoms, sex, age, profession, element_num)
    dis_res, dis_sym_predict, ipt =  disease_judge(main_sym, symptoms, sex, age, profession, disease_num)
    dis_sym_predict = dis_sym_predict.iloc[:1] 
    ele_sym_predict = ele_sym_predict.iloc[:4]
   
    ele_idx = np.setdiff1d(ele_sym_predict.index, dis_sym_predict.index)
    ele_sym_predict = ele_sym_predict.loc[ele_idx].sort_values("pred", ascending=False)
    sym_ret = pd.concat([dis_sym_predict, ele_sym_predict.iloc[:3- dis_sym_predict.index.size]])
    return pd2dict(ele_res, "prob"), pd2dict(dis_res, "prob"), pd2dict(sym_ret, "pred") ,ipt

def get_main_symptoms(request):
    name = request.GET['name']
    sym_class = pd.read_pickle("database/sym_class.pkl")
    class_name = pd.read_pickle("database/class_name.pkl")    
    cls = class_name.index[class_name == name][0]
    sym = sym_class[sym_class["cls"] == cls]
    common_sym = pd.read_pickle("database/common_symptom.pkl")
    idx = np.intersect1d(common_sym.index, sym["sym"].values)    
    ret = common_sym.loc[idx].sort_values("freq", ascending=False)["name"]

    jsn = []
    for i in ret.index:
        jsn.append([i, ret[i]])
    return HttpResponse(json.dumps(jsn, ensure_ascii=False),content_type='application/json')

def index(request):
    context = {"title":"智能化中医症状采集器"}
    return  render(request, 'auto_tcm/auto_tcm.html', context)

def get_result(request):
    sex = int(request.GET['sex'])
    age = int(request.GET['age'])
    profession = 1 - int(request.GET['common'])    
    sym = json.loads(request.GET['symptoms'])
    main_sym = int(request.GET['main-symptom']) 
    symptoms = {}
    for s in sym:
        symptoms[int(s)] = int(sym[s])
    ret = {}
    ret["ele"], ret["dis"], ret["sym"], _ = get_judgement(main_sym, symptoms, sex, age, profession, 15, 8)
    return HttpResponse(json.dumps(ret, ensure_ascii=False),content_type='application/json')


def auto_ask(request):
    sex = int(request.GET['sex'])
    age = int(request.GET['age'])
    profession = 1 - int(request.GET['common'])
    symptom = {int(request.GET['main-symptom']):2}
    main_sym = int(request.GET['main-symptom'])
    context = {}
    context["sex"] = "女" if sex == 0 else "男"
    context["title"] = "智能化中医症状采集器" 
    context["main_sym_name"] = request.GET['main-symptom-name']
    context["main_sym"] = request.GET['main-symptom']
    res = {}   
    res["ele"], res["dis"], res["sym"], _ = get_judgement(main_sym, symptom, sex, age, profession, 15, 8)
    context["diagnose"] = json.dumps(res, ensure_ascii=False)
    context["num_array"] = list(range(len(res["sym"])))

    return  render(request, 'auto_tcm/auto_ask.html', context)