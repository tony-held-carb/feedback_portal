def quote_lines(input_filename="text_input.txt", output_filename="text_output.txt"):
  with open(input_filename, 'r', encoding='utf-8') as infile, \
      open(output_filename, 'w', encoding='utf-8') as outfile:
    for line in infile:
      stripped_line = line.rstrip('\n')
      quoted_line = f'"{stripped_line}",\n'
      outfile.write(quoted_line)


if __name__ == '__main__':
  # Example usage:
  quote_lines()
