# Held-out check for the highlighting mapping (spike 1, Q12): code the mapping was not tuned on.
# For each file in LIST, writes Rouge's HTML in the markup kramdown gives a fenced block, as a
# baseline dump would (OUT/base/dump/content/ID.html), and the same code as a fenced block for
# Folia to render (OUT/site/ID.md); prints the IDs. See README.md.
#
#   cd ../filopoe && bundle exec ruby PATH/heldout.rb LIST ROOT OUT
#
# A LIST line is "LANGUAGE PATH": PATH is relative to ROOT, or "rouge:NAME" for the demo Rouge
# ships for NAME.
require "fileutils"
require "rouge"

list, root, out = ARGV
demos = File.join(Gem.loaded_specs["rouge"].full_gem_path, "lib/rouge/demos")
FileUtils.mkdir_p([File.join(out, "base/dump/content"), File.join(out, "site")])

File.readlines(list, chomp: true).each_with_index do |line, i|
  lang, path = line.split(" ", 2)
  file = path.start_with?("rouge:") ? File.join(demos, path.delete_prefix("rouge:")) : File.join(root, path)
  code = File.read(file)
  code += "\n" unless code.end_with?("\n")
  id = format("%03d-%s-%s", i, lang, File.basename(file).tr(".", "_"))

  html = Rouge::Formatters::HTML.new.format(Rouge::Lexer.find(lang).new.lex(code))
  File.write(File.join(out, "base/dump/content/#{id}.html"),
    %(<div class="language-#{lang} highlighter-rouge"><div class="highlight">) +
    %(<pre class="highlight"><code>#{html}</code></pre></div></div>\n))

  fence = "`" * [3, (code.scan(/`+/).map(&:size).max || 0) + 1].max
  File.write(File.join(out, "site/#{id}.md"), "#{fence}#{lang}\n#{code}#{fence}\n")
  puts id
end
