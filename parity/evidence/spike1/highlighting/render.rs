// The renderer for review.py: a throwaway binary crate depending on `folia-core` by path, run
// as `hl-dump SITE OUT SOURCE...` (see README.md).
// Renders the given sources of a site with Folia's Markdown, for the highlighting review.
use folia_core::content::markdown::to_html;
use folia_core::content::split_front_matter;
fn main() {
    let args: Vec<String> = std::env::args().collect();
    let (site, out) = (&args[1], &args[2]);
    for source in &args[3..] {
        let text = std::fs::read_to_string(format!("{site}/{source}")).unwrap();
        let body = split_front_matter(&text).map_or(text.as_str(), |(_, b)| b);
        let path = format!("{out}/{source}.html");
        std::fs::create_dir_all(std::path::Path::new(&path).parent().unwrap()).unwrap();
        std::fs::write(path, to_html(body, None)).unwrap();
    }
}
