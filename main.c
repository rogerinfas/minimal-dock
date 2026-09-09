#include <gtk/gtk.h>
#include <gtk-layer-shell.h>
#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static GtkWidget *clock_label;
static GtkWidget *dnd_label;
static GtkWidget *dnd_btn;

static gboolean update_clock(gpointer user_data) {
    time_t rawtime;
    struct tm *timeinfo;
    char buffer[16];

    time(&rawtime);
    timeinfo = localtime(&rawtime);
    strftime(buffer, sizeof(buffer), "%H:%M", timeinfo);

    gtk_label_set_text(GTK_LABEL(clock_label), buffer);
    return TRUE;
}

static gboolean get_dnd_state(void) {
    FILE *fp = popen("swaync-client -D 2>/dev/null", "r");
    if (!fp) return FALSE;
    char buffer[32];
    gboolean is_dnd = FALSE;
    if (fgets(buffer, sizeof(buffer), fp) != NULL) {
        if (strstr(buffer, "true") != NULL) {
            is_dnd = TRUE;
        }
    }
    pclose(fp);
    return is_dnd;
}

static gboolean update_dnd_status(gpointer user_data) {
    gboolean is_dnd = get_dnd_state();
    GtkStyleContext *ctx = gtk_widget_get_style_context(dnd_btn);
    if (is_dnd) {
        gtk_label_set_text(GTK_LABEL(dnd_label), "󰂛"); // Campana silenciada
        gtk_widget_set_tooltip_text(dnd_btn, "No Molestar: Activo (Clic para desactivar)");
        gtk_style_context_remove_class(ctx, "dnd-off");
        gtk_style_context_add_class(ctx, "dnd-on");
    } else {
        gtk_label_set_text(GTK_LABEL(dnd_label), "󰂚"); // Campana normal
        gtk_widget_set_tooltip_text(dnd_btn, "No Molestar: Desactivado (Clic para activar)");
        gtk_style_context_remove_class(ctx, "dnd-on");
        gtk_style_context_add_class(ctx, "dnd-off");
    }
    return TRUE;
}

static void toggle_dnd(GtkWidget *widget, gpointer data) {
    system("swaync-client -d >/dev/null 2>&1 &");
    update_dnd_status(NULL);
}

static GdkMonitor* get_primary_monitor(void) {
    GdkDisplay *display = gdk_display_get_default();
    if (!display) return NULL;
    GdkMonitor *primary = gdk_display_get_primary_monitor(display);
    if (primary) return primary;

    int n = gdk_display_get_n_monitors(display);
    if (n == 0) return NULL;

    GdkMonitor *best_monitor = gdk_display_get_monitor(display, 0);
    int max_pixels = 0;
    for (int i = 0; i < n; i++) {
        GdkMonitor *mon = gdk_display_get_monitor(display, i);
        GdkRectangle geom;
        gdk_monitor_get_geometry(mon, &geom);
        int pixels = geom.width * geom.height;
        if (pixels > max_pixels) {
            max_pixels = pixels;
            best_monitor = mon;
        }
    }
    return best_monitor;
}

int main(int argc, char *argv[]) {
    gtk_init(&argc, &argv);

    GtkWidget *win = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_widget_set_name(win, "dock-window");

    gtk_layer_init_for_window(GTK_WINDOW(win));
    gtk_layer_set_namespace(GTK_WINDOW(win), "minimal-dock");
    gtk_layer_set_layer(GTK_WINDOW(win), GTK_LAYER_SHELL_LAYER_OVERLAY);

    GdkMonitor *mon = get_primary_monitor();
    if (mon) {
        gtk_layer_set_monitor(GTK_WINDOW(win), mon);
    }

    gtk_layer_set_anchor(GTK_WINDOW(win), GTK_LAYER_SHELL_EDGE_BOTTOM, TRUE);
    gtk_layer_set_anchor(GTK_WINDOW(win), GTK_LAYER_SHELL_EDGE_LEFT, FALSE);
    gtk_layer_set_anchor(GTK_WINDOW(win), GTK_LAYER_SHELL_EDGE_RIGHT, FALSE);
    gtk_layer_set_anchor(GTK_WINDOW(win), GTK_LAYER_SHELL_EDGE_TOP, FALSE);
    gtk_layer_set_margin(GTK_WINDOW(win), GTK_LAYER_SHELL_EDGE_BOTTOM, 14);

    GdkScreen *screen = gtk_widget_get_screen(win);
    GdkVisual *visual = gdk_screen_get_rgba_visual(screen);
    if (visual && gdk_screen_is_composited(screen)) {
        gtk_widget_set_visual(win, visual);
    }
    gtk_widget_set_app_paintable(win, TRUE);

    // Cargar CSS
    GtkCssProvider *provider = gtk_css_provider_new();
    char css_path[512];
    snprintf(css_path, sizeof(css_path), "%s/.config/minimal-dock/style.css", getenv("HOME"));
    gtk_css_provider_load_from_path(provider, css_path, NULL);
    gtk_style_context_add_provider_for_screen(screen, GTK_STYLE_PROVIDER(provider), GTK_STYLE_PROVIDER_PRIORITY_APPLICATION);

    // UI Box
    GtkWidget *box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 0);
    GtkStyleContext *box_ctx = gtk_widget_get_style_context(box);
    gtk_style_context_add_class(box_ctx, "dock-capsule");

    clock_label = gtk_label_new("");
    gtk_style_context_add_class(gtk_widget_get_style_context(clock_label), "dock-clock");
    gtk_box_pack_start(GTK_BOX(box), clock_label, TRUE, TRUE, 0);

    dnd_btn = gtk_button_new();
    gtk_style_context_add_class(gtk_widget_get_style_context(dnd_btn), "dock-dnd-btn");
    dnd_label = gtk_label_new("󰂚");
    gtk_container_add(GTK_CONTAINER(dnd_btn), dnd_label);
    g_signal_connect(dnd_btn, "clicked", G_CALLBACK(toggle_dnd), NULL);
    gtk_box_pack_start(GTK_BOX(box), dnd_btn, FALSE, FALSE, 0);

    gtk_container_add(GTK_CONTAINER(win), box);

    update_clock(NULL);
    update_dnd_status(NULL);

    g_timeout_add_seconds(1, update_clock, NULL);
    g_timeout_add_seconds(2, update_dnd_status, NULL);

    g_signal_connect(win, "destroy", G_CALLBACK(gtk_main_quit), NULL);
    gtk_widget_show_all(win);
    gtk_main();

    return 0;
}
