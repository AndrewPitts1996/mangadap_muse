;+
; NAME:
;       MDAP_INITIALIZATION_BLOCK
;
; PURPOSE:
;   MAIN BLOCK FOR MANGA_DAP:
;       - Execute the user-define setup that defines how the DAP should
;         be executed and the locations of the template libraries,
;         emission-line parameter files, and spectral-index parameter
;         files.
;       - Initialize all the I/O paths.
;       - Build the ExecutionPlan structures.
;
; CALLING SEQUENCE:
;       MDAP_INITIALIZATION_BLOCK, manga_dap_version, tpl_library_keys, template_libraries, $
;                                  tpl_vacuum_wave, ems_line_keys, emission_line_parameters, $
;                                  ems_vacuum_wave, abs_line_keys, absorption_line_parameters, $
;                                  abs_vacuum_wave, execution_plan, plate, ifudesign, mode, $
;                                  velocity_initial_guess, velocity_dispersion_initial_guess, ell, $
;                                  pa, Reff, datacube_name, output_file_root, n_tpl_lib, $
;                                  inptbl=inptbl, index=index, par=par, drppath=drppath, $
;                                  dappath=dappath, dapsrc=dapsrc, $
;                                  save_intermediate_steps=save_intermediate_steps, $
;                                  remove_null_templates=remove_null_templates, $
;                                  bvls_shared_lib=bvls_shared_lib, nolog=nolog, $
;                                  log_file_unit=log_file_unit, quiet=quiet
;
; INPUTS:
;       manga_dap_version MaNGADAPVersion
;               Structure used to keep track of various
;               version-controlled procedures in the DAP.
;      
; OPTIONAL INPUTS:
;       inptbl string
;           File with the input table providing the necessary input
;           parameters.  See MDAP_CREATE_INPUT_TABLE for the file
;           format.  Should not be provided along with par.  Must also
;           provide index for use.
;
;       index integer
;           Row index in inptbl with the parameters to use.
;
;       par string
;           SDSS par (yanny) file with the parameters to use.  Read
;           using YANNY_READONE(), meaning that only the first entry
;           will be read, but others can be present.
;
;       drppath string
;           Path to the DRP-produced file.  The name of the file MUST be
;           manga-[plate]-[ifudesign]-LOG[mode].fits (or .fits.gz).
;           This optional sets the path to this file.  See
;           MDAP_READ_INPUT_SETUP for the default path.
;
;       dappath string
;           Path to the root directory for the DAP output files.  The
;           output files will be placed in dappath/plate/ifudesign/ with
;           each file having the root name
;           manga-[plate]-[ifudesign]-LOG[mode]_; see MDAP_SETUP_IO.
;           See MDAP_READ_INPUT_SETUP for the default path.
;
;       dapsrc string
;           Path the the DAP source directory.  Used in
;           MDAP_EXECUTION_SETUP to set the paths to the template
;           libraries, etc.
;
;       save_intermediate_steps  integer
;               Flag to save intermediate steps in the DAP.  CURRENTLY
;               OBSOLETE.  Kept because it may come into use later.
;
;       remove_null_templates integer
;               Flag to remove templates from consideration with zero
;               weight.  CURRENTLY OBSOLETE.  Kept because it may come
;               into use later.
;
;       bvls_shared_lib string
;               Path to the external FORTRAN library, which contains the fortran
;               versions of mdap_bvls.pro.  If not specified, or if the path is
;               invalid, the default internal IDL mdap_bvls code is used. 
;
;       log_file_unit LUN
;               File unit pointing to the log file
;
; OPTIONAL KEYWORDS:
;       /nolog
;               Suppress output to the log file.
;
;       /quiet
;               Suppress output to the screen.
;
; OUTPUT:
;       tpl_library_keys strarr[]
;               Set of keywords used to uniquely select template
;               libraries.
;
;       template_libraries strarr[]
;               Path definitions for each of the libraries.
;
;       tpl_vacuum_wave intarr[]
;               Flag that wavelengths of each template library is (1) or
;               is not (0) in vacuum.
;
;       ems_line_keys strarr[]
;               Set of keywords used to uniquely select emission-line
;               parameter sets.
;
;       emission_line_parameters strarr[]
;               Path definitions for each of the emission-line parameter
;               sets.
;               
;       ems_vacuum_wave intarr[]
;               Flag that wavelengths of each emission-line parameter set
;               is (1) or is not (0) in vacuum.
;
;       abs_line_keys strarr[]
;               Set of keywords used to uniquely select spectral-index
;               parameter sets.
;
;       absorption_line_parameters strarr[]
;               Path definitions for each of the spectral-index parameter
;               sets.
;               
;       abs_vacuum_wave intarr[]
;               Flag that wavelengths of each spectral-index parameter
;               set is (1) or is not (0) in vacuum.
;
;       execution_plan ExecutionPlan[]
;               Array of structures providing a set of plans and
;               parameters as needed for each of the requested series of
;               analysis steps.
;
;       plate integer
;               Plate number for object to analyze.
;
;       ifudesign integer
;               IFU design number for object to analyze.
;
;       mode string
;               Mode ('RSS' or 'CUBE') of the data reduction to analyze.
;
;       velocity_initial_guess double
;               Initial guess for the velocity when fitting the
;               kinematics.
;
;       velocity_dispersion_initial_guess double
;               Initial guess for the velocity dispersion when fitting
;               the kinematics.
;
;       ell double
;               Ellipticity of the isophotal contours.
;
;       pa double
;               Position angle of the isophotal contours.
;
;       Reff double
;               Semi-major axis radius enclosing 50% of the galaxy light.
;
;       datacube_name string
;               Name of the DRP (RSS or CUBE) fits file to read.
;
;       output_file_root string
;               Root name for all DAP output files from this run.
;
;       n_tpl_lib integer
;               Total number of template libraries available.
;       
; OPTIONAL OUTPUT:
;
; COMMENTS:
;
; EXAMPLES:
;
; BUGS:
;
; PROCEDURES CALLED:
;       MDAP_EXECUTION_SETUP
;       MDAP_READ_INPUT_SETUP
;       MDAP_SETUP_IO
;       MDAP_LOG_INSTANTIATE
;       MDAP_DRP_CHECK_FILETYPE
;       MDAP_CHECK_FILE_EXISTS()
;       MDAP_BUILD_EXECUTION_PLANS
;       MDAP_PRINT_EXECUTION_PLAN
;
; REVISION HISTORY:
;       01 Feb 2015: Pulled from manga_dap.pro by K. Westfall (KBW)
;       10 Feb 2015: (KBW) Moved definition of template libraries,
;                          emission-line parameter files, and
;                          spectral-index parameter files to their own
;                          procedures, allowing for global effective
;                          edits.  MDAP_EXECUTION_SETUP should now
;                          return KEYWORDS for the selected files, NOT
;                          INDICES.  The MDAP_SELECTED_KEYWORD_INDEX
;                          function then converts those keywords into
;                          the appropriate index.
;       17 Mar 2015: (KBW) Allow to read execution plan from parameter
;                          file.  When not provided, default plan(s)
;                          created (MDAP_SURVEY_EXECUTION_SETUP) and the
;                          plan parameter file is written to disk.
;                          Removed save_intermediate_steps and
;                          remove_null_templates (not used anyway).
;                          Moved external_library definition from
;                          mdap_execution_setup to here, now hard-wired.
;                          Moved definition of dapsrc to here from
;                          MDAP_SURVEY_EXECUTION_SETUP.  signifier
;                          removed from MDAP_SURVEY_EXECUTION_SETUP; now
;                          hard-wired as the name of the written plan
;                          file.
;       28 Aug 2015: (KBW) Changed the name of the plan file to reflect
;                          the changes in the python components of the
;                          DAP.
;-
;------------------------------------------------------------------------

PRO MDAP_INITIALIZATION_BLOCK, $
        manga_dap_version, tpl_library_keys, template_libraries, tpl_vacuum_wave, ems_line_keys, $
        emission_line_parameters, ems_vacuum_wave, abs_line_keys, absorption_line_parameters, $
        abs_vacuum_wave, execution_plan, plate, ifudesign, mode, velocity_initial_guess, $
        velocity_dispersion_initial_guess, ell, pa, Reff, datacube_name, output_file_root, $
        n_tpl_lib, inptbl=inptbl, index=index, par=par, plan=plan, drppath=drppath, $
        dappath=dappath, dapsrc=dapsrc, bvls_shared_lib=bvls_shared_lib, nolog=nolog, $
        log_file_unit=log_file_unit, quiet=quiet

;       save_intermediate_steps=save_intermediate_steps, $
;       remove_null_templates=remove_null_templates,

        ;----------------------------------------------------------------
        ; Read the input parameters
        MDAP_READ_INPUT_SETUP, inptbl=inptbl, index=index, par=par, drppath=drppath, $
                               dappath=dappath, plate, ifudesign, mode, velocity_initial_guess, $
                               velocity_dispersion_initial_guess, ell, pa, Reff, root_name, $
                               output_root_dir

        ;----------------------------------------------------------------
        ; Set input file names and output directory
        ;     make the directory if it doesn't exist
        ; TODO: Allow for a single spectrum mode
        MDAP_SETUP_IO, root_name, output_root_dir, datacube_name, file_root, output_dir, $
                       output_file_root

        ;----------------------------------------------------------------
        ; Define the available template library and parameter files
        MDAP_DEFINE_AVAILABLE_TEMPLATE_LIBRARIES, tpl_library_keys, template_libraries, $
                                                  tpl_vacuum_wave, dapsrc=dapsrc
        MDAP_DEFINE_AVAILABLE_EMISSION_LINE_PARAMETERS, ems_line_keys, emission_line_parameters, $
                                                        ems_vacuum_wave, dapsrc=dapsrc
        MDAP_DEFINE_AVAILABLE_SPECTRAL_INDEX_PARAMETERS, abs_line_keys, $
                                                         absorption_line_parameters, $
                                                         abs_vacuum_wave, dapsrc=dapsrc

        ;----------------------------------------------------------------
        ; Define the DAP source path
        if n_elements(dapsrc) eq 0 then $
            dapsrc = getenv('MANGADAP_DIR')

        ;----------------------------------------------------------------
        ; Define the external library.  This is currently HARD-WIRED!
        external_library=dapsrc+'/external/F90_64/'

        ; Check the external library has an appropriate shared-object
        ; library
        if n_elements(external_library) ne 0 then begin
            bvls_shared_lib=external_library+'bvls.so'
            if file_test(bvls_shared_lib) eq 0 then $
                bvls_shared_lib=external_library+'bvls.dylib'
            if file_test(bvls_shared_lib) eq 0 then begin
                print, 'WARNING: Shared object library does not exist! Continuing by using IDL' $
                       + 'bvls routine.'
                ; Undefine the variables
                tempvar = size(temporary(external_library))
                tempvar = size(temporary(bvls_shared_lib))
            endif
        endif

        ;----------------------------------------------------------------
        ; Get the details of the execution plan
        if n_elements(plan) eq 0 then begin
            ; Execute the script the sets the user-level execution
            ; parameters tpl_lib_analysis, ems_par_analysis, and
            ; abs_par_analysis are string-based keywords that select the
            ; libraries above.
            MDAP_SURVEY_EXECUTION_SETUP, mode, bin_par, w_range_sn, threshold_ston_bin, $
                                         w_range_analysis, threshold_ston_analysis, analysis, $
                                         tpl_lib_analysis, ems_par_analysis, abs_par_analysis, $
                                         analysis_par, analysis_prior, overwrite_flag, execute_flag

            plan = output_dir + '/mangadap-' + MDAP_STC(plate, /integer) + '-' $
                   + MDAP_STC(ifudesign, /integer) + '-LOG' + mode + '-plan.par'

            MDAP_WRITE_EXECUTION_PLANS, plan, bin_par, w_range_sn, threshold_ston_bin, $
                                        w_range_analysis, threshold_ston_analysis, analysis, $
                                        tpl_lib_analysis, ems_par_analysis, abs_par_analysis, $
                                        analysis_par, analysis_prior, overwrite_flag, $
                                        execute_flag, /overwrite
        endif else begin
            ; Read the execution plan from a file
            MDAP_READ_EXECUTION_PLANS, plan, bin_par, w_range_sn, threshold_ston_bin, $
                                       w_range_analysis, threshold_ston_analysis, analysis, $
                                       tpl_lib_analysis, ems_par_analysis, abs_par_analysis, $
                                       analysis_par, analysis_prior, overwrite_flag, execute_flag
        endelse

        ;-----------------------------------------------------------------------
        ; These calls use a function that converts the selected keywords
        ; to the index in the available list; the input keywords are
        ; overwritten!
        tpl_lib_analysis = MDAP_SELECTED_KEYWORD_INDEX(tpl_library_keys, tpl_lib_analysis)
        ems_par_analysis = MDAP_SELECTED_KEYWORD_INDEX(ems_line_keys, ems_par_analysis)
        abs_par_analysis = MDAP_SELECTED_KEYWORD_INDEX(abs_line_keys, abs_par_analysis)

;       ; TODO: save_intermediate_steps and remove_null_templates are not used
;       ; Check if save_intermediate_steps exits, if not set to not save intermediate steps
;       if n_elements(save_intermediate_steps) eq 0 then $
;           save_intermediate_steps = 0

;       ; Check if remove_null_elemens exits, if not set to remove null templates
;       if n_elements(remove_null_templates) eq 0 then $
;           remove_null_templates = 0

;       ; TODO: Need to pass log_file_unit to other subroutines?

        ;-----------------------------------------------------------------------
        ; Instantiate the log file
        if ~keyword_set(nolog) then begin
            MDAP_LOG_INSTANTIATE, output_dir, manga_dap_version.main, plan, datacube_name, $
                                  mode, file_root, velocity_initial_guess, $
                                  velocity_dispersion_initial_guess, ell, pa, Reff, log_file_unit, $
                                  inptbl=inptbl, index=index, par=par
        endif

        ; Check that the mode makes sense with the data format
        MDAP_DRP_CHECK_FILETYPE, datacube_name, mode

        ;-----------------------------------------------------------------------
        ; TODO: Same as ntpl_libraries, neml_files, and nabs_files in mdap_execution_setup

        ; Check data read from the library and parameter file definitions
        n_tpl_lib = n_elements(template_libraries)          ; Number of template libraries
        n_ems_par = n_elements(emission_line_parameters)    ; Number of emission-line files
        n_abs_par = n_elements(absorption_line_parameters)  ; Number of spectral-index files

        ; Need /search tag, because 'template_libraries' are search based strings
        success = MDAP_CHECK_FILE_EXISTS(template_libraries, /search)   ; Aborts if fails
        if success ne 0 then $
            message, 'Template libraries not correctly defined.'
                
        success = MDAP_CHECK_FILE_EXISTS(emission_line_parameters)
        if success ne 0 then $
            message, 'Emission-line parameter files not correctly defined.'

        success = MDAP_CHECK_FILE_EXISTS(absorption_line_parameters)
        if success ne 0 then $
            message, 'Absorption-line parameter files not correctly defined.'


        ;-----------------------------------------------------------------------
        ; Build the ExecutionPlan structures based on the user input
        MDAP_BUILD_EXECUTION_PLANS, version=manga_dap_version.execute_plan  ; Version control

        MDAP_BUILD_EXECUTION_PLANS, n_tpl_lib, n_ems_par, n_abs_par, bin_par, ell, pa, Reff, $
                                    w_range_sn, threshold_ston_bin, w_range_analysis, $
                                    threshold_ston_analysis, analysis, analysis_par, $
                                    analysis_prior, tpl_lib_analysis, ems_par_analysis, $
                                    abs_par_analysis, overwrite_flag, execute_flag, $
                                    output_file_root, execution_plan

        ; Report the ExecutionPlans to the user for review
        n_plans = n_elements(execution_plan)
        if ~keyword_set(quiet) then begin
            for i=0,n_plans-1 do begin
                print, 'EXECUTION PLAN: ', i+1
                MDAP_PRINT_EXECUTION_PLAN, template_libraries, emission_line_parameters, $
                                           absorption_line_parameters, execution_plan[i]
            endfor
        endif

        ; Print some details to the log file
        if ~keyword_set(nolog) then begin
            printf, log_file_unit, '[INFO] Execution plans built using version: ', $
                    manga_dap_version.execute_plan
            printf, log_file_unit, '[INFO] Number of plans to execute: ', n_plans
        endif

END

