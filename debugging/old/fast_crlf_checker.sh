#!/bin/bash
echo "=== Fast CRLF vs LF Checker ==="
echo "Checking line endings for files in file_extension_matches.txt..."

# Create the table header
cat > crlf_lf_table.txt << 'EOF'
# Table: Files with CRLF vs LF Line Endings
| File Number | Relative Path | Line Ending Format |
|-------------|---------------|-------------------|
EOF

# Skip the header lines in file_extension_matches.txt and process each file
counter=1
tail -n +3 file_extension_matches.txt | while IFS= read -r file; do
    if [ -n "$file" ] && [ -f "$file" ]; then
        # Check line ending format using file command
        line_ending=$(file "$file" | grep -o "CRLF\|LF\|no line terminators" || echo "UNKNOWN")
        
        # Add to table
        printf "| %d | %s | %s |\n" "$counter" "$file" "$line_ending" >> crlf_lf_table.txt
        
        counter=$((counter + 1))
        
        # Show progress every 100 files
        if [ $((counter % 100)) -eq 0 ]; then
            echo -n "."
        fi
    fi
done

echo ""
echo "=== Summary ==="
echo "Total files analyzed: $((counter - 1))"

# Count CRLF vs LF files
crlf_count=$(grep "CRLF" crlf_lf_table.txt | wc -l)
lf_count=$(grep "LF" crlf_lf_table.txt | wc -l)
unknown_count=$(grep "UNKNOWN\|no line terminators" crlf_lf_table.txt | wc -l)

echo "Files with CRLF line endings: $crlf_count"
echo "Files with LF line endings: $lf_count"
echo "Files with unknown/no line terminators: $unknown_count"

echo ""
echo "=== Sample of CRLF files ==="
grep "CRLF" crlf_lf_table.txt | head -10

echo ""
echo "=== Sample of LF files ==="
grep "LF" crlf_lf_table.txt | head -10

echo ""
echo "Results saved to crlf_lf_table.txt" 