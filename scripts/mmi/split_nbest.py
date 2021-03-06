# encoding: utf-8
"""
@author: Yuxian Meng
@contact: yuxian_meng@shannonai.com

@version: 1.0
@file: split_nbest
@time: 2020/12/26 22:05
@desc: split nbest list from fairseq-generate to multiple files,
       which will be used to compute Mutual information.

       target-dir
          └── rank0
                └── src-tgt.src
                └── src-tgt.tgt
                └── scores.forward
          └── rank1
          ...
"""

import argparse
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nbest-file", type=str, help="nbest file generated by generate.py")
    parser.add_argument("--target-dir", type=str, help="target dir to store splitted nbest predictions")
    parser.add_argument("--nbest", type=int, help="the n of 'n'best")
    args = parser.parse_args()
    output_files = []
    for i in range(args.nbest):
        subdir = os.path.join(args.target_dir, f"rank{i}")
        os.makedirs(subdir, exist_ok=True)
        output_files.append([
            open(os.path.join(subdir, "src-tgt.src"), "w"),
            open(os.path.join(subdir, "src-tgt.tgt"), "w"),
            open(os.path.join(subdir, "scores.forward"), "w")
        ])

    file_idx = 0
    count = 0
    with open(args.nbest_file) as fin:
        for line in fin:
            # write last line of origin input as tgt file
            if line.startswith("L"):
                for i in range(args.nbest):
                    output_files[i][1].write(" ".join(line.split()[1:])+"\n")
                count += 1
            # write predict as src file and store in scores.forward
            elif line.startswith("H"):
                data = line.split()
                score = data[1]
                src = " ".join(data[2:])
                output_files[file_idx][0].write(src+"\n")
                output_files[file_idx][2].write(score+"\n")
                file_idx = (file_idx+1) % args.nbest

    for i in range(args.nbest):
        for f in output_files[i]:
            f.close()
    print(f"Wrote {count} source/target/scores to {args.nbest} sub directories in {args.target_dir}")


if __name__ == '__main__':
    main()
