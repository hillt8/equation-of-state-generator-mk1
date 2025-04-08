!/bin/bash

# Step 1: Create results directory
mkdir -p results

# Step 2: Data collection from u folder
cd u

for dir in x y z; do
    output_file="u$dir.txt"
    > "../results/$output_file"

    for i in {0..10}; do
        i_val=$(printf "%.1f" $i)
        for j in 0.95 0.96 0.97 0.98 0.99 1.00 1.01 1.02 1.03 1.04 1.05 1.06 1.07 1.08 1.09 1.10; do 
            if [ -d "$i_val/$dir/$j/" ]; then
                if tac "$i_val/$dir/$j/vasp_output" | grep -q "reached required accuracy - stopping structural energy minimisation"; then
                    echo -n "$i_val $j " >> "../results/$output_file"
                    tac "$i_val/$dir/$j/vasp_output" | grep -m1 'F=' >> "../results/$output_file"
                else
                    echo "$i_val $j no data found!" >> "../results/$output_file"
                fi 
            else
                echo "$i_val $j directory not found!" >> "../results/$output_file"
            fi
        done 
    done

done
cd ..

# Step 3: Data collection from d3u folder
cd d3u

for dir in x y z; do
    output_file="d3u$dir.txt"
    > "../results/$output_file"

    for i in {0..10}; do
        i_val=$(printf "%.1f" $i)
        for j in 0.95 0.96 0.97 0.98 0.99 1.00 1.01 1.02 1.03 1.04 1.05 1.06 1.07 1.08 1.09 1.10; do 
            if [ -d "$i_val/$dir/$j/" ]; then
                if tac "$i_val/$dir/$j/vasp_output" | grep -q "reached required accuracy - stopping structural energy minimisation"; then
                    echo -n "$i_val $j " >> "../results/$output_file"
                    tac "$i_val/$dir/$j/vasp_output" | grep -m1 'F=' >> "../results/$output_file"
                else
                    echo "$i_val $j no data found!" >> "../results/$output_file"
                fi 
            else
                echo "$i_val $j directory not found!" >> "../results/$output_file"
            fi
        done 
    done

done
cd ..
