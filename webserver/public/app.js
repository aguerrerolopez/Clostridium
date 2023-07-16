(function() {
    var isInternetExplorer = /MSIE | Trident\//.test(window.navigator.userAgent);

    /* Loading state in forms */
    $('form:not([data-loading="false"])').on('submit', function() {
        const $formBtn = $(this).find('button[type="submit"]');
        $formBtn.prop('disabled', true)
            .attr('data-original', $formBtn.html())
            .html('<span class="spinner-border spinner-border-sm"></span>');
    });

    /* Localization of timestamps */
    $('time[datetime]').each(function() {
        var $this = $(this);
        $this.text(moment.unix($this.attr('datetime')).format('YYYY-MM-DD HH:mm:ss'));
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
                    var file = new File([blob], 'samples.zip');
                    uploadFile(file);
                });
                return;
            }

            // Upload ZIP archive
            var file = files[0];
            if (file.isFile) {
                file.file(function(vanillaFile) {
                    uploadFile(vanillaFile);
                });
            } else {
                uploadFile(file);
            }
        };

        /**
         * @param {File} file File instance
         */
        var uploadFile = function(file) {
            var UPLOADING_MESSAGE = 'Uploading...';
            var PROCESSING_MSG = 'Processing...';
            showFeedbackUploading(UPLOADING_MESSAGE, 0);

            // Fix progress bar in IE
            if (isInternetExplorer) {
                $uploadArea.find('.progress .progress-bar').css('transition', 'none');
            }

            // Send file to server
            var payload = new FormData();
            payload.append('samples', file);
            $.ajax({
                type: 'post',
                url: document.location.href,
                data: payload,
                processData: false,
                contentType: false,
                xhr: function() {
                    var xhr = new window.XMLHttpRequest();
                    xhr.upload.addEventListener('progress', function(e) {
                        if (e.lengthComputable) {
                            var progress = (e.loaded / e.total) * 100;
                            var message = (progress < 100) ? UPLOADING_MESSAGE : PROCESSING_MSG;
                            showFeedbackUploading(message, progress);
                        }
                    }, false);
                    return xhr;
                }
            }).done(function(data) {
                var $feedbackDone = $uploadArea.find('.feedback-done');
                $feedbackDone.find('.report').html(data.report);
                $uploadArea.find('.feedback-uploading').addClass('d-none');
                $feedbackDone.removeClass('d-none');
            }).fail(function(e) {
                if (e.status === 413) {
                    showFeedbackError('The uploaded file is too large');
                } else {
                    showFeedbackError('Unexpected error');
                }
            });
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
            $uploadArea.find('.feedback-initial, .feedback-uploading').addClass('d-none');
            $uploadArea.find('.feedback-error p.heading').html(message);
            $uploadArea.find('.feedback-error').removeClass('d-none');
        };

        /**
         * @param {string} message  Message
         * @param {number} progress Progress between 0 and 100
         */
        var showFeedbackUploading = function(message, progress) {
            $uploadArea.find('.feedback-initial').addClass('d-none');
            $uploadArea.find('.feedback-uploading p.heading').html(message);
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

    /* Results page */
    var $resultsFilters = $('form.results-filters');
    if ($resultsFilters.length > 0) {
        var $fromInput = $resultsFilters.find('input[name="from"]');
        var $toInput = $resultsFilters.find('input[name="to"]');

        // Handle date picker
        var $datePicker = $resultsFilters.find('.date-picker');
        $datePicker.on('change', function() {
            if ($fromInput.val() === '') {
                $(this).val('Any date');
            }
        });
        $datePicker.daterangepicker({
            startDate: ($fromInput.val() === '') ? undefined : moment.unix($fromInput.val()),
            endDate: ($toInput.val() === '') ? undefined : moment.unix($toInput.val()),
            minYear: 2010,
            maxDate: moment().endOf('day'),
            autoApply: true,
            locale: {
                format: 'YYYY-MM-DD',
                firstDay: 1
            }
        }, function(from, to) {
            $fromInput.val(from.unix());
            $toInput.val(to.unix());
        });

        // Handle change number results per page
        $('select.results-limit').on('change', function() {
            document.location.href = $(this).val();
        });

        // Handle checkboxes
        var refreshCheckboxes = function() {
            var totalSamples = $('.results-table tbody input[type="checkbox"]').length;
            var selectedSamples = $('.results-table tbody input[type="checkbox"]:checked').map(function() {
                return $(this).parents('tr').data('sample');
            }).get();

            // Update selected sample count and form data
            $('.selected-samples-count').text((selectedSamples.length === 1) ?
                '1 sample selected' :
                selectedSamples.length + ' samples selected'
            );
            $('button.btn-download-zip, button.btn-export-csv').prop('disabled', selectedSamples.length === 0);
            $('form.results-download input[name="samples"]').val(selectedSamples.join(','));

            // Update status of "all samples" checkbox
            var isChecked = (selectedSamples.length === totalSamples);
            var isIndeterminate = (selectedSamples.length > 0) && !isChecked;
            $('#all-samples').prop('indeterminate', isIndeterminate).prop('checked', isChecked);
        };
        $('.results-table thead input[type="checkbox"]').on('change', function() {
            $('.results-table tbody input[type="checkbox"]').prop('checked', $(this).prop('checked'));
            refreshCheckboxes();
        });
        $('.results-table tbody input[type="checkbox"]').on('change', function() {
            refreshCheckboxes();
        });
        $(document).ready(function() {
            refreshCheckboxes();
        });

        // Handle change sample label
        $('.results-table .label-wrapper select').on('change', function() {
            var $this = $(this);
            $this.prop('disabled', true);
            $.post('/results/' + $this.parents('tr').data('sample'), {
                label: $this.val()
            }).done(function(res) {
                $this.parents('.label-wrapper').text(res.labelName);
            }).fail(function() {
                $this.prop('disabled', false);
                $this.val('');
                alert('Failed to update label, please try again later')
            });
        });
        $('.results-table .label-wrapper .btn-confirm').click(function() {
            var $this = $(this);
            var $wrapper = $this.parents('.label-wrapper');
            $wrapper.find('button').prop('disabled', true);
            $.post('/results/' + $this.parents('tr').data('sample'), {
                label: $this.data('label')
            }).done(function(res) {
                $wrapper.text(res.labelName);
            }).fail(function() {
                $wrapper.find('button').prop('disabled', false);
                alert('Failed to update label, please try again later')
            });
        });
        $('.results-table .label-wrapper .btn-wrong').click(function() {
            var $wrapper = $(this).parents('.label-wrapper');
            $wrapper.find('.btn-group').remove();
            $wrapper.find('select').removeClass('d-none');
        });

        // Handle delete sample
        $('.results-table .btn-delete').click(function() {
            var $row = $(this).parents('tr');
            var $modal = $('#deleteModal');
            $modal.find('.sample-name').text($row.find('.sample-name').text());
            $modal.find('.inuse-message').toggleClass('d-none', !$row.data('inuse'));
            $modal.find('.btn-confirm-delete').data('sample', $row.data('sample'));
            $modal.modal();
        });
        $('#deleteModal .btn-confirm-delete').click(function() {
            var $this = $(this);
            $this.html('<span class="spinner-border spinner-border-sm"></span>').prop('disabled', true);
            $.ajax({
                method: 'DELETE',
                url: '/results/' + $this.data('sample')
            }).fail(function() {
                alert('Failed to delete sample, please try again later');
            }).always(function() {
                window.location.reload();
            });
        });

        // Handle reload button
        $('.btn-reload').click(function(e) {
            e.preventDefault();
            window.location.reload();
        });
    }

    /* Single result page */
    var $resultPage = $('.result-page');
    if ($resultPage.length > 0) {
        // Handle change sample name
        var $heading = $resultPage.find('.heading');
        $heading.find('button.btn-edit').click(function() {
            $heading.find('h2').addClass('d-none');
            $heading.find('form').removeClass('d-none');
        });
        $heading.find('button.btn-cancel').click(function() {
            $heading.find('form').addClass('d-none');
            $heading.find('h2').removeClass('d-none');
        });

        // Handle change sample label
        $resultPage.find('select.select-label').change(function() {
            var $this = $(this);
            $this.prop('disabled', true);
            $.post(document.location.href, {
                label: $this.val()
            }).fail(function() {
                $this.val('');
                alert('Failed to update label, please try again later')
            }).always(function() {
                $this.prop('disabled', false);
            });
        });
    }
})();
