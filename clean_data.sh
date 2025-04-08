#!/bin/bash

mkdir -p results/clean

process_set() {
    local prefix=$1
    local out_file="results/clean/${prefix}.txt"
    local fx="results/${prefix}x.txt"
    local fy="results/${prefix}y.txt"
    local fz="results/${prefix}z.txt"

    awk '
    function extract_e0(start, end, fields) {
        for (i = start; i <= end; i++) {
            if (fields[i] == "E0=" && i+1 <= end) {
                return fields[i+1]
            }
        }
        return "error"
    }
    FNR==NR { fx[FNR]=$0; next }
    NR>FNR && NR<=FNR+length(fx) { fy[FNR]=$0; next }
    NR>FNR+length(fx) {
        split(fx[FNR], xfields, " ")
        split(fy[FNR], yfields, " ")
        split($0, zfields, " ")

        x = extract_e0(1, 7, xfields)
        y = extract_e0(1, 7, yfields)
        z = extract_e0(1, 7, zfields)

        printf "%s %s %s %s %s\n", xfields[1], xfields[2], x, y, z
    }
    ' "$fx" "$fy" "$fz" > "$out_file"
}

# Run cleaning
process_set u
process_set d3u

echo "x y z data compiled in u.txt and d3u.txt"

