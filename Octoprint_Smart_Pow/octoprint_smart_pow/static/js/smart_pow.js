$(function() {
    function SmartPowViewModel(parameters) {
        var self = this;

        self.settings = parameters[0];
        self.power_state = "unknown"
        // console.log("HARRY POTTER IS BACK")
        // console.log(self.settings)

        // this will hold the URL currently displayed by the iframe
        // self.currentUrl = ko.observable();

        // this will hold the URL entered in the text field
        // self.newUrl = ko.observable();

        // this will be called when the user clicks the "Go" button and set the iframe's URL to
        // the entered URL
        self.goToUrl = function() {
            // self.currentUrl(self.newUrl());
        };

        self.get_power_state = function() {
            console.log("Querying API for power state")
            OctoPrint.simpleApiGet("simple_pow")
            .then(function (data) {
                power_state = data["power_state"]
                self.power_state(power_state)
            }).fail(function (err) {
                console.log(err)
            })

        }
        // This will get called before the HelloWorldViewModel gets bound to the DOM, but after its
        // dependencies have already been initialized. It is especially guaranteed that this method
        // gets called _after_ the settings have been retrieved from the OctoPrint backend and thus
        // the SettingsViewModel been properly populated.
        self.onBeforeBinding = function() {
            // self.newUrl(self.settings.settings.plugins.helloworld.url());
            // self.goToUrl();
            setInterval(self.get_power_state,1000)
        }
    }

    // This is how our plugin registers itself with the application, by adding some configuration
    // information to the global variable OCTOPRINT_VIEWMODELS
    OCTOPRINT_VIEWMODELS.push(
        {
            // This is the constructor to call for instantiating the plugin
            construct: SmartPowViewModel,
            // This is a list of dependencies to inject into the plugin, the order which you request
            // here is the order in which the dependencies will be injected into your view model upon
            // instantiation via the parameters argument
            dependencies: ["settingsViewModel"],
            // Finally, this is the list of selectors for all elements we want this view model to be bound to.
            elements: ["#tab_plugin_smart_pow"]
        });
});
