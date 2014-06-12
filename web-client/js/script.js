var conferenceAnalyzerModule = angular.module('conferenceAnalyzer', ['mm.foundation']);

conferenceAnalyzerModule.service('ConferenceAnalyzerService', ["$http",
    function($http) {
        //this.prefix = "http://apps.jlcanovas.es/jsonDiscoverer";
        this.prefix = "http://localhost:8080/fr.inria.atlanmod.conferenceanalysis.services/";
        //this.prefix = "http://localhost:8080/jsonDiscoverer";

        this.callPostService = function(call, dataToSend, success, failure) {
            $http({
                method : 'POST',
                url : call,
                data : dataToSend,
                headers : {'Content-Type': 'application/x-www-form-urlencoded'}
            }).success(function(data) {
                success(data);
            }).error(function(data, status, headers, config) {
                failure(data, status, headers, config);
            });
        };

        this.callGetService = function(call, success, failure) {
            $http({
                method : 'GET',
                url : call
            }).success(function(data) {
                success(data);
            }).error(function(data, status, headers, config) {
                failure(data, status, headers, config);
            });
        };

        this.getConferences = function(success, failure) {
            this.callGetService(this.prefix + "/conferences", success, failure);
        }

        this.getAuthorsPapersPerConference = function(conferenceName, success, failure) {
            var dataToSend = $.param( {
                conference : conferenceName
            });

            this.callPostService(this.prefix + "/authorsPapersPerConference", dataToSend, success, failure);
        }

        this.getLocationsPerConference = function(conferenceName, success, failure) {
            var dataToSend = $.param( {
                conference : conferenceName
            });

            this.callPostService(this.prefix + "/locationsPerConference", dataToSend, success, failure);
        }
    }
]);

conferenceAnalyzerModule.controller("ConferenceCtrl", ["$scope", "ConferenceAnalyzerService",
    function($scope, ConferenceAnalyzerService) {
        $scope.conferenceSelected = undefined;
        $scope.conferences = undefined;
        $scope.sigmaInstance = undefined;
        $scope.layoutRunning = false;

        $scope.getConferences = function() {
            if($scope.conferences == undefined) {
                var retrievedConferences = []
                ConferenceAnalyzerService.getConferences(
                    function(data) {
                        angular.forEach(data.conferences, function(item) {
                            retrievedConferences.push(item);
                        });
                        console.log("Success");
                    },
                    function(data) {
                        retrievedConferences.push("No conferences could be retrieved");
                        console.log("No conferences");
                    }
                );
                $scope.conferences = retrievedConferences;
            } 
            return $scope.conferences;
        };

        $scope.search = function() {
            ConferenceAnalyzerService.getAuthorsPapersPerConference(
                $scope.conferenceSelected,
                function(data) {
                    /*if($scope.sigmaInstance != undefined) {
                        $scope.sigmaInstance.clear();
                    }*/
                    var parser = new DOMParser();
                    var domElement = parser.parseFromString(data, 'application/xml');
                    sigma.parsers.gexf(
                        domElement,
                        {
                            container : 'graph'
                        },
                        function(instance) {
                            $scope.sigmaInstance = instance
                        }
                    );
                },
                function(data) {
                    console.log("No graph retrieved");
                }
            );
        };

        document.getElementById("layout").addEventListener("click", function() {
            if($scope.sigmaInstance != undefined) {
                if($scope.layoutRunning) {
                    $scope.layoutRunning = false;
                    document.getElementById("layout").innerHTML = 'Start Layout';
                    $scope.sigmaInstance.stopForceAtlas2();
                } else {
                    $scope.layoutRunning = true;
                    document.getElementById("layout").innerHTML = 'Stop Layout';
                    $scope.sigmaInstance.startForceAtlas2();
                }
            }
        });
    }
]);

conferenceAnalyzerModule.controller("MapCtrl", ["$scope", "ConferenceAnalyzerService",
    function($scope, ConferenceAnalyzerService) {
        $scope.map = kartograph.map('#map');
        $scope.map.loadMap('world.svg', function(map) { 
            map.addLayer('world', {
                styles: {
                    fill: '#fff',
                    stroke: '#000',
                    'stroke-width': 0.7
                }
            });
        });

        $scope.search = function() {
            ConferenceAnalyzerService.getLocationsPerConference(
                $scope.conferenceSelected,
                function(data) {
                    color = chroma.scale('Blues').domain(data,5,'quantiles','popularity');
                    $scope.map.addLayer('world', {
                        styles: {
                            'stroke-width': 0.7,
                            fill: function(d) { 
                                return color(data[d.iso3]?data[d.iso3].popularity:0); 
                            },
                            stroke: function(d) {
                                return color(data[d.iso3]?data[d.iso3].popularity:0).darker();
                            }
                        }
                    });
                },
                function(data) {
                    console.log("No location information retrieved");
                }
            );
        };
    }
]);


/*function initGraph() {
    var sigmaInstance = null;

    sigma.renderers.def = sigma.renderers.canvas;
    sigma.parsers.gexf(
        'data.gexf',
        {
            container : 'graph'
        },
        function(instance) {
            sigmaInstance = instance
        }
    );

    var layoutRunning = false;
    document.getElementById("layout").addEventListener("click", function() {
        if(layoutRunning) {
            layoutRunning = false;
            document.getElementById("layout").innerHTML = 'Start Layout';
            sigmaInstance.stopForceAtlas2();
        } else {
            layoutRunning = true;
            document.getElementById("layout").innerHTML = 'Stop Layout';
            sigmaInstance.startForceAtlas2();
        }
    });

    document.getElementById('rescale').addEventListener('click',function(){
        sigmaInstance.position(0,0,1).draw();
    },true);
    //sigma.plugins.dragNodes(sigmaInstance, sigmaInstance.renderers[0]);
    //sigmaGraph.draw();
}

if(document.addEventListener) {
    document.addEventListener("DOMContentLoaded", initGraph, false);
} else {
    window.onload = initGraph;
}*/
