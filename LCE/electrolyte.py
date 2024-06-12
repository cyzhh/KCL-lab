import pandas as pd
import requests
from bs4 import BeautifulSoup


def search_pubchem_by_name(compound_name):
    base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
    query_url = f"{base_url}compound/name/{compound_name}/cids/json"
    
    response = requests.get(query_url)
    
    if response.status_code == 200:
        cids = response.json()["IdentifierList"]["CID"]
        if cids:
            print(f"找到了化合物ID: {', '.join(map(str, cids))}")
            return cids
        else:
            print("没有找到匹配的化合物ID。")
    else:
        print("查询失败，状态码：", response.status_code)
        
def get_smiles_and_mw(cid):
    base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
    
    smiles_query_url = f"{base_url}compound/cid/{cid}/property/CanonicalSMILES/json"
    mw_query_url = f"{base_url}compound/cid/{cid}/property/MolecularWeight/json"
    
    smiles_response = requests.get(smiles_query_url)
    mw_response = requests.get(mw_query_url)
    
    if smiles_response.status_code == 200 and mw_response.status_code == 200:
        smiles = smiles_response.json()['PropertyTable']['Properties'][0]['CanonicalSMILES']
        mw = mw_response.json()['PropertyTable']['Properties'][0]['MolecularWeight']
        return smiles, mw
    else:
        print("查询失败。")
        return None, None

def get_solvent(cid):
    base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
    base_url2 = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/"
    
    smiles_query_url = f"{base_url}compound/cid/{cid}/property/CanonicalSMILES/json"
    mw_query_url = f"{base_url}compound/cid/{cid}/property/MolecularWeight/json"
    density_query_url = f"{base_url2}compound/{cid}/JSON/?heading=Chemical+and+Physical+Properties"
    smiles_response = requests.get(smiles_query_url)
    mw_response = requests.get(mw_query_url)
    density_response = requests.get(density_query_url)
    
    if smiles_response.status_code == 200 and mw_response.status_code == 200 and density_response.status_code == 200:
        smiles = smiles_response.json()['PropertyTable']['Properties'][0]['CanonicalSMILES']
        mw = mw_response.json()['PropertyTable']['Properties'][0]['MolecularWeight']
        mw = float(mw)

        data = density_response.json()
        for section in data["Record"]["Section"]:
            if section.get("TOCHeading") == "Chemical and Physical Properties":
                for ss in section.get("Section"):
                    if ss.get("TOCHeading") == "Experimental Properties":
                        for sss in ss.get("Section"):
                            if sss.get("TOCHeading") == "Density":
                                density = sss.get("Information")[0]["Value"]["StringWithMarkup"][0]["String"]
                                density = float(density)
            break  
        return smiles, mw, density
    else:
        print("查询失败。")
        return None, None, None


if __name__ == "__main__":

    ### 数据读取
    train_path = "dataset/train.xlsx"
    appendix1_path = "dataset/appendix1.xlsx"
    appendix2_path = "dataset/appendix2.xlsx"
    train_data = pd.read_excel(train_path)
    appendix1_data = pd.read_excel(appendix1_path)
    appendix2_data = pd.read_excel(appendix2_path)

    ### input
    mol_salt_num = input("请输入盐的摩尔数：")
    salt = input("请输入盐的名称：")
    solvents = input("请输入电解液：").split(" ")
    percentages = input("请输入配比：").split(":")
    
    electrolyte = []
    tmp_solvent = []
    
    ### 处理盐并加入电解液配比electrolyte
    #### ToDo 暂时还没有考虑多盐 
    salt_row = appendix2_data[appendix2_data['Salt'] == salt]
    if not salt_row.empty:
        smiles = salt_row['SMILES'].iloc[0]
        electrolyte.append((smiles, mol_salt_num))
    else:
        print("没有找到与输入盐名匹配的行。")
        #### 添加没有的盐加入数据库  ToDo 暂时还没有保存至appendix2.xlsx 因为需要考察这个盐是不是脏数据  后面接入PubChempy
        cid = search_pubchem_by_name(salt)[0]
        smiles, molecular_weight = get_smiles_and_mw(cid)
        if smiles and molecular_weight is not None:
            new_row = {'Salt':salt,'MW':molecular_weight,'SMILES':smiles}
            appendix2_data = appendix2_data._append(new_row, ignore_index=True)
            electrolyte.append((smiles, mol_salt_num))
        else:
            print("未能获取到SMILES或分子量信息。")

    ### 处理电解液并加入电解液配比electrolyte
    for solvent in solvents:
        if solvent:
            solvent_row = appendix1_data[appendix1_data['Solvent'] == solvent]
            if not solvent_row.empty:
                smiles = solvent_row['SMILES'].iloc[0]
                mol = float(solvent_row['mol/L'].iloc[0])
                tmp_solvent.append((smiles,mol))
            else:
                print("没有找到与输入电解液名匹配的行。")
                cid = search_pubchem_by_name(solvent)[0]
                smiles, molecular_weight, density = get_solvent(cid)
                if smiles and molecular_weight and density is not None:
                    new_row = {
                        'Solvent':solvent,
                        'MW':molecular_weight,
                        'density (g/mL)':density,
                        'mol/L':density/molecular_weight*1000,
                        'SMILES':smiles}
                    # print(new_row)
                    appendix2_data = appendix2_data._append(new_row, ignore_index=True)
                    tmp_solvent.append((smiles, mol_salt_num))
                else:
                    print("未能获取到SMILES或分子量信息。")

    # print(tmp_solvent)
    sum1 = 0
    for i in range(len(percentages)):
        if percentages[i]:
            mol = float(tmp_solvent[i][1].strip()) * float(percentages[i].strip())
            electrolyte.append((tmp_solvent[i][0],mol))
    
    print("电解液配比：",electrolyte)
    
