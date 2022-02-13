$(function() {
    function SmartPowViewModel(parameters) {
        var self = this;

        self.settings = parameters[0];
        self.power_state = ko.observable('')
        self.is_conditional_power_off_enabled = ko.observable('')
        // TODO declare constants and keys at the top

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

        // TODO: I've noticed a bug that on server startup, the web-UI
        // will keep showing 'Unknown' untill a power_state button is clicked
        self.get_state_from_server = function() {
            OctoPrint.simpleApiGet("smart_pow")
            .then(function (data) {
                // TODO make this data key a constant
                self.power_state(data["power_state"])
                self.is_conditional_power_off_enabled(data["automatic_power_off_enabled"])
                // If the server doesn't know
                // then let's ask it after a backoff
                backoff = 1000
                if(data["power_state"] == "Unknown") {
                    setTimeout(self.get_state_from_server,backoff)
                }
            }).fail(function (err) {
                console.log(err)
            })
        }



        self.turn_on = function() {
            OctoPrint.simpleApiCommand("smart_pow","set_power_state",{
                power_state: "On"
            })
            .then(function (data) {
                // power_state = data["power_state"]
                // self.power_state(power_state)
            }).fail(function (err) {
                console.log(err)
            })
        }

        self.turn_off = function() {
            OctoPrint.simpleApiCommand("smart_pow","set_power_state",{
                power_state: "Off"
            })
            .then(function (data) {
                // power_state = data["power_state"]
                // self.power_state(power_state)
            }).fail(function (err) {
                console.log(err)
            })
        }
        // This will get called before the HelloWorldViewModel gets bound to the DOM, but after its
        // dependencies have already been initialized. It is especially guaranteed that this method
        // gets called _after_ the settings have been retrieved from the OctoPrint backend and thus
        // the SettingsViewModel been properly populated.
        self.onBeforeBinding = function() {
            self.get_state_from_server()
        }

        self.onEventplugin_smart_pow_power_state_changed_event = function(payload) {
            self.power_state(payload["power_state"])
        }
        self.onEventplugin_smart_pow_conditional_power_off_changed_event = function(payload) {
            // TODO value-check the payload. It should be a boolean type
            self.is_conditional_power_off_enabled(payload["automatic_power_off_enabled"])
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
