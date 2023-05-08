(function() {
    /* Loading state in forms */
    var $forms = document.querySelectorAll('form');
    for (var i=0; i<$forms.length; i++) {
        var $form = $forms[i];
        $form.addEventListener('submit', function() {
            const $formBtn = this.querySelector('button[type="submit"]');
            $formBtn.disabled = true;
            $formBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
        });
    }

    /* Upload page */
    var $uploadArea = document.querySelector('.upload-area');
    if ($uploadArea !== null) {
        /** @return {boolean} Whether upload area is locked or not */
        var isLocked = function() {
            return $uploadArea.classList.contains('locked');
        }

        /**
         * @param {(File|FileSystemFileEntry)[]} files Files or file entries
         */
        var onFiles = function(files) {
            $uploadArea.classList.add('locked');

            // Check for empty list of files (IE limitation)
            if (files.length === 0) {
                showFeedbackError('Your browser does not support uploading folders, please create a ZIP archive and upload that');
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
            $uploadArea.querySelector('.feedback-initial').classList.add('d-none');
            $uploadArea.querySelector('.feedback-error p').innerHTML = message;
            $uploadArea.querySelector('.feedback-error').classList.remove('d-none');
        };

        /**
         * @param {string} message  Message
         * @param {number} progress Progress between 0 and 100
         */
        var showFeedbackUploading = function(message, progress) {
            $uploadArea.querySelector('.feedback-initial').classList.add('d-none');
            $uploadArea.querySelector('.feedback-uploading p').innerHTML = message;
            $uploadArea.querySelector('.feedback-uploading .progress-bar').style = 'width:'+progress+'%';
            $uploadArea.querySelector('.feedback-uploading').classList.remove('d-none');
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
        $uploadArea.addEventListener('click', function() {
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
            $uploadArea.classList.add('hover');
        });
        document.documentElement.addEventListener('dragleave', function(e) {
            e.preventDefault();
            $uploadArea.classList.remove('hover');
        });
        document.documentElement.addEventListener('dragend', function(e) {
            e.preventDefault();
            $uploadArea.classList.remove('hover');
        });
        document.documentElement.addEventListener('drop', function(e) {
            e.preventDefault();
            $uploadArea.classList.remove('hover');
            if (!isLocked()) {
                scanDataTransfer(e.dataTransfer).then(function(files) {
                    onFiles(files);
                });
            }
        });

        // Handle try again button
        $uploadArea.querySelector('.feedback-error button').addEventListener('click', function(e) {
            e.stopImmediatePropagation();
            $uploadArea.querySelector('.feedback-error').classList.add('d-none');
            $uploadArea.querySelector('.feedback-initial').classList.remove('d-none');
            $uploadArea.classList.remove('locked');
        });
    }
})();
