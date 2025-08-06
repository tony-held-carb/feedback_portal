#!/bin/bash
echo "=== Counting Files with CRLF vs LF Line Endings ==="
echo ""

# Create the table header
cat > crlf_lf_analysis.txt << 'EOF'
# Table: Files with CRLF vs LF Line Endings
| File Number | Relative Path | Line Ending Format |
|-------------|---------------|-------------------|
EOF

# Initialize counter
counter=1

# Find all files with specified extensions and check their line endings
find . -type f -not -path "./.git/*" -not -path "./.idea/*" \( -name "*.py" -o -name "*.txt" -o -name "*.md" -o -name "*.json" -o -name "*.html" -o -name "*.css" -o -name "*.js" -o -name "*.sh" -o -name "*.yml" -o -name "*.yaml" -o -name "*.xml" -o -name "*.sql" -o -name "*.ini" -o -name "*.cfg" -o -name "*.conf" \) | while IFS= read -r file; do
    if [ -f "$file" ]; then
        # Get relative path (remove leading ./)
        relative_path=$(echo "$file" | sed 's|^\./||')
        
        # Check line ending format
        line_ending=$(file "$file" | grep -o "CRLF\|LF\|no line terminators" || echo "UNKNOWN")
        
        # Add to table
        printf "| %d | %s | %s |\n" "$counter" "$relative_path" "$line_ending" >> crlf_lf_analysis.txt
        
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
crlf_count=$(grep "CRLF" crlf_lf_analysis.txt | wc -l)
lf_count=$(grep "LF" crlf_lf_analysis.txt | wc -l)
unknown_count=$(grep "UNKNOWN\|no line terminators" crlf_lf_analysis.txt | wc -l)

echo "Files with CRLF line endings: $crlf_count"
echo "Files with LF line endings: $lf_count"
echo "Files with unknown/no line terminators: $unknown_count"

echo ""
echo "=== Sample of CRLF files ==="
grep "CRLF" crlf_lf_analysis.txt | head -10

echo ""
echo "=== Sample of LF files ==="
grep "LF" crlf_lf_analysis.txt | head -10

echo ""
echo "Results saved to crlf_lf_analysis.txt" 