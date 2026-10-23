# ggplot2 theme for divergences.  In a post:
#   source("../../assets/theme_divergences.R")
#   p + theme_divergences("light")      # or "dark" (use with #| renderings: [light, dark])
#   p + scale_colour_divergences()      # the blog's series colours, in their tested order
#
# Colours match assets/viz.js (validated for colour-blind separation and contrast).

divergences_colours <- list(
  light = list(bg = "#e9f3f4", ink = "#0c2a33", ink2 = "#3a5860", muted = "#526c75", grid = "#d3e3e6",
               series = c("#0a8fa8", "#c0662a", "#6a4bc4", "#a87d00", "#2f6fc0", "#0f8a66"),
               cool = "#0a8fa8", neutral = "#d6e3e5", warm = "#c0662a"),
  dark  = list(bg = "#081a20", ink = "#e1f0f2", ink2 = "#a7c3c8", muted = "#86a6ad", grid = "#16323a",
               series = c("#1aa3bb", "#cf7036", "#8e77e4", "#b88b0c", "#5a8bdc", "#279f78"),
               cool = "#1aa3bb", neutral = "#24393f", warm = "#cf7036")
)

theme_divergences <- function(mode = c("light", "dark"), base_size = 12) {
  mode <- match.arg(mode)
  k <- divergences_colours[[mode]]
  ggplot2::theme_minimal(base_size = base_size) +
    ggplot2::theme(
      plot.background = ggplot2::element_rect(fill = k$bg, colour = NA),
      panel.background = ggplot2::element_rect(fill = k$bg, colour = NA),
      panel.grid.major = ggplot2::element_line(colour = k$grid, linewidth = 0.3),
      panel.grid.minor = ggplot2::element_blank(),
      text = ggplot2::element_text(colour = k$ink2),
      axis.text = ggplot2::element_text(colour = k$muted),
      plot.title = ggplot2::element_text(colour = k$ink, face = "bold"),
      plot.subtitle = ggplot2::element_text(colour = k$muted),
      legend.position = "top", legend.justification = "left",
      strip.text = ggplot2::element_text(colour = k$ink, face = "bold")
    )
}

scale_colour_divergences <- function(mode = "light", ...) {
  ggplot2::scale_colour_manual(values = divergences_colours[[mode]]$series, ...)
}
scale_fill_divergences <- function(mode = "light", ...) {
  ggplot2::scale_fill_manual(values = divergences_colours[[mode]]$series, ...)
}
