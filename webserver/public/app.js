(function() {
    /* Loading state in forms */
    $('form').on('submit', function() {
        const $formBtn = $(this).find('button[type="submit"]');
        $formBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm"></span>');
    });

    /* Upload page */
    var $uploadArea = $('.upload-area');
    if ($uploadArea.length > 0) {
        /** @return {boolean} Whether upload area is locked or not */
        var isLocked = function() {
            return $uploadArea.hasClass('locked');
        }

        /**
         * @param {(File|FileSystemFileEntry)[]} files Files or file entries
         */
        var onFiles = function(files) {
            $uploadArea.addClass('locked');

            // Check for empty list of files
            if (files.length === 0) {
                var isInternetExplorer = /MSIE | Trident\//.test(window.navigator.userAgent);
                showFeedbackError(
                    isInternetExplorer ?
                    'Your browser does not support uploading folders, please create a ZIP archive and upload that' :
                    'Cannot upload an empty folder'
                );
                return;
            }

            // Validate files
            var numOfZipArchives = 0;
            var numOfRegularFiles = 0;
            for (var i=0; i<files.length; i++) {
                if (/\.zip$/i.test(files[i].name)) {
                    numOfZipArchives++;
                } else {
                    numOfRegularFiles++;
                }
            }
            if (numOfZipArchives > 1) {
                showFeedbackError('You cannot upload more than one ZIP archive at once');
                return;
            }
            if (numOfZipArchives > 0 && numOfRegularFiles > 0) {
                showFeedbackError('Either drop a ZIP file or a folder, not both at the same time');
                return;
            }
            if (numOfRegularFiles === 1) {
                showFeedbackError('Drop all files from the sample folder, not just one');
                return;
            }

            // Create ZIP archive
            if (numOfRegularFiles > 0) {
                showFeedbackUploading('Preparing files...', 0);
                createZip(files).then(function(blob) {
                    // TODO: upload `Blob`
                });
                return;
            }

            // Upload ZIP archive
            // TODO: upload `File`
        };

        /**
         * @param  {FileSystemFileEntry[]} entries File entries
         * @return {Promise<Blob>}                 ZIP archive
         */
        var createZip = function(entries) {
            return new Promise(function(resolve) {
                var zip = new JSZip();
                var promises = [];
                for (var i=0; i<entries.length; i++) {
                    var promise = new Promise(function(resolveEntry) {
                        var entry = entries[i];
                        var filepath = entry.fullPath.slice(1);
                        entry.file(function(file) {
                            file.arrayBuffer().then(function(buffer) {
                                zip.file(filepath, buffer, {
                                    date: new Date(file.lastModified)
                                });
                                resolveEntry();
                            });
                        });
                    });
                    promises.push(promise);
                }
                Promise.all(promises).then(function() {
                    zip.generateAsync({type: 'blob'}).then(resolve);
                });
            });
        };

        /**
         * @param {string} message Message
         */
        var showFeedbackError = function(message) {
            $uploadArea.find('.feedback-initial').addClass('d-none');
            $uploadArea.find('.feedback-error p').html(message);
            $uploadArea.find('.feedback-error').removeClass('d-none');
        };

        /**
         * @param {string} message  Message
         * @param {number} progress Progress between 0 and 100
         */
        var showFeedbackUploading = function(message, progress) {
            $uploadArea.find('.feedback-initial').addClass('d-none');
            $uploadArea.find('.feedback-uploading p').html(message);
            $uploadArea.find('.feedback-uploading .progress-bar').css('width', progress+'%');
            $uploadArea.find('.feedback-uploading').removeClass('d-none');
        };

        /**
         * @template T
         * @param  {Promise<T[]>[]} promises Promises
         * @return {Promise<T[]>}            Flattened promise
         */
        var flatPromises = function(promises) {
            return new Promise(function(resolve) {
                Promise.all(promises).then(function(results) {
                    var flatResults = [];
                    for (var i=0; i<results.length; i++) {
                        flatResults = flatResults.concat(results[i]);
                    }
                    resolve(flatResults);
                });
            });
        }

        /**
         * @param  {DataTransfer}                          dataTransfer Data transfer instance
         * @return {Promise<(File|FileSystemFileEntry)[]>}              All file entries
         */
        var scanDataTransfer = function(dataTransfer) {
            return new Promise(function(resolve) {
                if (dataTransfer.items) {
                    var promises = [];
                    for (var i=0; i<dataTransfer.items.length; i++) {
                        if (dataTransfer.items[i].kind !== 'file') {
                            continue;
                        }
                        if (dataTransfer.items[i].webkitGetAsEntry) {
                            var entry = dataTransfer.items[i].webkitGetAsEntry();
                            promises.push(scanEntry(entry));
                        } else {
                            promises.push(dataTransfer.items[i].getAsFile());
                        }
                    }
                    flatPromises(promises).then(resolve);
                } else {
                    resolve(dataTransfer.files);
                }
            });
        }

        /**
         * @param  {FileSystemEntry}               item Root entry
         * @return {Promise<FileSystemFileEntry[]>}     All file entries
         */
        var scanEntry = function(item) {
            return new Promise(function(resolve) {
                if (item.isDirectory) {
                    item.createReader().readEntries(function(entries) {
                        var promises = [];
                        for (var i=0; i<entries.length; i++) {
                            promises.push(scanEntry(entries[i]));
                        }
                        flatPromises(promises).then(function(res) {
                            resolve(res);
                        });
                    });
                } else {
                    resolve([item]);
                }
            });
        };

        // Handle select file manually
        $uploadArea.click(function() {
            if (isLocked()) return;
            var input = document.createElement('input');
            input.type = 'file';
            input.accept = '.zip';
            input.addEventListener('change', function(e) {
                onFiles(e.target.files);
            });
            input.click();
        });

        // Handle drag and drop
        document.documentElement.addEventListener('dragover', function(e) {
            e.preventDefault();
            $uploadArea.addClass('hover');
        });
        document.documentElement.addEventListener('dragleave', function(e) {
            e.preventDefault();
            $uploadArea.removeClass('hover');
        });
        document.documentElement.addEventListener('dragend', function(e) {
            e.preventDefault();
            $uploadArea.removeClass('hover');
        });
        document.documentElement.addEventListener('drop', function(e) {
            e.preventDefault();
            $uploadArea.removeClass('hover');
            if (!isLocked()) {
                scanDataTransfer(e.dataTransfer).then(function(files) {
                    onFiles(files);
                });
            }
        });

        // Handle try again button
        $uploadArea.find('.feedback-error button').click(function(e) {
            e.stopImmediatePropagation();
            $uploadArea.find('.feedback-error').addClass('d-none');
            $uploadArea.find('.feedback-initial').removeClass('d-none');
            $uploadArea.removeClass('locked');
        });
    }
})();
