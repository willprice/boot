    #!/usr/bin/env python
    #-*- coding:utf-8 -*-
    
    import gtk, webkit
    
    # set of methods for the help tab browser
    def delete_event(widget, event, data=None):
        return False
    def destroy(widget, data=None):
        gtk.main_quit()
    
    def go_back(widget, data=None):
        browser.go_back()
    def go_forward(widget, data=None):
        browser.go_forward()
    def go_home(widget, data=None):
        browser.open("http://www.google.com")
    def load_www(widge, data=None):
        url = www_adr_bar.get_text()
        try:
            url.index("://")
        except:
            url = "http://" + url
        www_adr_bar.set_text(url)
        browser.open(url)
    def update_buttons(widget, data=None):
        www_adr_bar.set_text( widget.get_main_frame().get_uri() )
        back_button.set_sensitive(browser.can_go_back())
        forward_button.set_sensitive(browser.can_go_forward())
    def load_progress_amount(webview, amount):
        progress.set_fraction(amount/100.0)
    def load_started(webview, frame):
        progress.set_visible(True)
    def load_finished(webview, frame):
        progress.set_visible(False)
    
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.set_size_request(920, 600)
    win.connect("delete_event", delete_event)
    win.connect("destroy", destroy)
    win.set_resizable(True)
    
    scroller = gtk.ScrolledWindow()
    browser = webkit.WebView()
    browser.connect("load-progress-changed", load_progress_amount)
    browser.connect("load-started", load_started)
    browser.connect("load-finished", load_finished)
    browser.connect("load_committed", update_buttons)
    www_adr_bar = gtk.Entry()
    www_adr_bar.connect("activate", load_www)
    hlp_hbox = gtk.HBox()
    hlp_vbox = gtk.VBox()
    progress = gtk.ProgressBar()
    back_button = gtk.ToolButton(gtk.STOCK_GO_BACK)
    back_button.connect("clicked", go_back)
    forward_button = gtk.ToolButton(gtk.STOCK_GO_FORWARD)
    forward_button.connect("clicked", go_forward)
    home_button = gtk.ToolButton(gtk.STOCK_HOME)
    home_button.connect("clicked", go_home)
    # put help tab together
    hlp_hbox.pack_start(back_button,False, False,5)
    hlp_hbox.pack_start(forward_button,False, False)
    hlp_hbox.pack_start(home_button,False, False)
    hlp_hbox.pack_start(www_adr_bar,True, True)
    hlp_vbox.pack_start(hlp_hbox,False, False,10)
    hlp_vbox.pack_start(scroller,True, True)
    hlp_vbox.pack_start(progress,False, False)
    scroller.add(browser)
    
    default_www = 'http://www.google.com'
    www_adr_bar.set_text(default_www)
    
    # LOAD PAGE
    browser.open(default_www)
    
    back_button.set_sensitive(False)
    forward_button.set_sensitive(False)
    
    win.add(hlp_vbox)
    win.show_all()
    gtk.main()
    




