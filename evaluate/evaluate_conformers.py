from rdkit import Chem
import pickle
from rdkit.Chem import rdMolAlign
from rdkit.Chem.rdMolAlign import GetBestRMS
import statistics as stats
import glob
import os.path as osp
import argparse
from tqdm import tqdm

def open_ref_root(ref_root):
    print("parsing_root_ref")
    if ref_root is None:
        ref_root = "/data/ho70/GeoMol/data/QM9/qm9"
    all_files = sorted(glob.glob(osp.join(ref_root, '*.pickle')))
    pickle_files = [f for i, f in enumerate(all_files)] 
    mol_dic = {}
    for f in pickle_files:
        dic = open_pickle(f)
        name = dic["smiles"]
        conf_list = []
        for conf in dic['conformers']:
            conf_list.append(conf['rd_mol'])
        mol_dic[name] = conf_list
    
    # save to file
    with open("ref_mols.pkl", 'wb') as f:
        pickle.dump(mol_dic, f)

    return mol_dic 
    
def get_conf_cov_mat(test_smiles, test_dic, ref_dic, gamma=0.5):
    MAT_list = []
    COV_list =[]
    num_smiles = 0
    for smile in tqdm(test_smiles):
        test_conf_list = test_dic[smile]
        min_RMSD_list = []
        coverage_total = 0
        if smile in ref_dic:
            ref_conf_list = ref_dic[smile]
            try:
                for ref_conf in ref_conf_list:
                    RMSD_list = []
                    for test_conf in test_conf_list: 
                        ref_conf = Chem.RemoveHs(ref_conf)
                        test_conf = Chem.RemoveHs(test_conf)
                        RMSD_list.append(GetBestRMS(test_conf, ref_conf))
                    min_RMSD = min(RMSD_list)
                    min_RMSD_list.append(min_RMSD)
                    if min_RMSD < gamma:
                        coverage_total += 1
                MAT = sum(min_RMSD_list)/ len(ref_conf_list)
                COV = coverage_total/ len(ref_conf_list) *100
                #print(f"{smile}: COV {COV} MAT {MAT}")
                MAT_list.append(MAT)
                COV_list.append(COV)
                num_smiles += 1
            except:
                pass
    print(f"Number of smiles {num_smiles}")
    return COV_list, MAT_list


def open_pickle(mol_path):
    with open(mol_path, "rb") as f:
        dic = pickle.load(f)
    return dic
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to compute Cov and MAT scores and RMSD for single conformers')
    parser.add_argument('test_mol_dic', help='path to test molecules dictionary')
    parser.add_argument('--ref_dic', default=None)
    parser.add_argument('--ref_root', default=None)
    args = parser.parse_args()
    
    if args.ref_dic is None:
        ref_dic = open_ref_root(args.ref_root)
    else:
        ref_dic = open_pickle(args.ref_dic)

    test_dic = open_pickle(args.test_mol_dic)
    test_smiles = test_dic.keys()
    
    COV_list, MAT_list = get_conf_cov_mat(test_smiles, test_dic, ref_dic, gamma=0.5)
    print("Summary Results")
    print("Mean COV: " + str(stats.mean(COV_list)))
    print("Median COV: " + str(stats.median(COV_list)))
    print ("Maximum COV: " + str(max(COV_list)))
    print("Mean MAT: " + str(stats.mean(MAT_list)))
    print("Median MAT: " + str(stats.median(MAT_list)))
    print("Minimum MAT: " + str(min(MAT_list)))
    