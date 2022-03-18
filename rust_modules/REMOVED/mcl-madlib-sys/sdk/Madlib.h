#ifndef _MADLIB_H_
#define _MADLIB_H_

#define		MCL_SUCCESS				 0
#define     MCL_GENERAL_ERROR		-1
#define		MCL_DEV_ERROR			-2
#define		MCL_DEV_NOT_ATTACHED	-3
#define		MCL_USAGE_ERROR			-4
#define		MCL_DEV_NOT_READY		-5
#define		MCL_ARGUMENT_ERROR		-6
#define		MCL_INVALID_AXIS		-7
#define		MCL_INVALID_HANDLE		-8

#pragma pack(push, 1)
struct ProductInformation {
	unsigned char  axis_bitmap; //bitmap of available axis
	short ADC_resolution;		//# of bits of resolution
	short DAC_resolution;		//# of bits of resolution
	short Product_id;
	short FirmwareVersion;
	short FirmwareProfile;
};
#pragma pack(pop)

#ifdef __cplusplus
	extern"C"{
#else
	typedef unsigned char bool;
#endif

#define MADLIB_API __declspec(dllimport)

MADLIB_API	void	MCL_DLLVersion(short *version, short *revision);

MADLIB_API  int		MCL_InitHandle();
MADLIB_API  int		MCL_GrabHandle(short device);
MADLIB_API  int		MCL_InitHandleOrGetExisting();
MADLIB_API  int		MCL_GrabHandleOrGetExisting(short device);
MADLIB_API  int		MCL_GetHandleBySerial(short serial);
MADLIB_API  int		MCL_GrabAllHandles();
MADLIB_API  int		MCL_GetAllHandles(int *handles, int size);
MADLIB_API  int		MCL_NumberOfCurrentHandles();
MADLIB_API  void	MCL_ReleaseHandle(int handle);
MADLIB_API  void	MCL_ReleaseAllHandles();

MADLIB_API	double  MCL_SingleReadZ(int handle);
MADLIB_API	double	MCL_SingleReadN(unsigned int axis, int handle);
MADLIB_API	int		MCL_SingleWriteZ(double position, int handle);
MADLIB_API	int		MCL_SingleWriteN(double position, unsigned int axis, int handle);
MADLIB_API	double	MCL_MonitorZ(double position, int handle);
MADLIB_API	double	MCL_MonitorN(double position, unsigned int axis, int handle);
MADLIB_API	double	MCL_ReadEncoderZ(int handle);
MADLIB_API	int		MCL_ResetEncoderZ(int handle);
MADLIB_API	int		MCL_ThetaX(double milliradians, double *actual, int handle);
MADLIB_API	int		MCL_ThetaY(double milliradians, double *actual, int handle);
MADLIB_API	int		MCL_MoveZCenter(double position, double *actual, int handle);
MADLIB_API	int		MCL_LevelZ(double position, int handle);
MADLIB_API	int		MCL_CFocusSetFocusMode(bool focusModeOn, int handle);
MADLIB_API	int		MCL_CFocusStep(double relativePositionChange, int handle);
MADLIB_API	int		MCL_CFocusGetFocusMode(int *focusLocked, int handle);

MADLIB_API	int		MCL_ReadWaveFormN(unsigned int axis,unsigned int DataPoints,double milliseconds,double* waveform, int handle);
MADLIB_API	int		MCL_Setup_ReadWaveFormN(unsigned int axis,unsigned int DataPoints,double milliseconds, int handle);
MADLIB_API	int		MCL_Trigger_ReadWaveFormN(unsigned int axis,unsigned int DataPoints,double *waveform, int handle);
MADLIB_API	int		MCL_LoadWaveFormN(unsigned int axis,unsigned int DataPoints,double milliseconds,double* waveform, int handle);
MADLIB_API	int		MCL_Setup_LoadWaveFormN(unsigned int axis,unsigned int DataPoints,double milliseconds,double *waveform, int handle);
MADLIB_API	int		MCL_Trigger_LoadWaveFormN(unsigned int axis, int handle);
MADLIB_API	int		MCL_TriggerWaveformAcquisition(unsigned int axis, unsigned int DataPoints, double* waveform, int handle);

MADLIB_API  int     MCL_WfmaSetup(double *wfDacX, double *wfDacY, double *wfDacZ, int dataPointsPerAxis, double milliseconds, unsigned short iterations, int handle);
MADLIB_API  int     MCL_WfmaTriggerAndRead(double *wfAdcX, double *wfAdcY, double *wfAdcZ, int handle);
MADLIB_API  int     MCL_WfmaTrigger(int handle);
MADLIB_API  int     MCL_WfmaRead(double *wfAdcX, double *wfAdcY, double *wfAdcZ, int handle);
MADLIB_API  int     MCL_WfmaStop(int handle);

MADLIB_API	int		MCL_IssBindClockToAxis(int clock, int mode, int axis, int handle);
MADLIB_API	int		MCL_IssConfigurePolarity(int clock, int mode, int handle);
MADLIB_API	int		MCL_IssSetClock(int clock, int mode, int handle);
MADLIB_API	int		MCL_IssResetDefaults(int handle);
MADLIB_API	int		MCL_ChangeClock(double milliseconds, short clock, int handle);
MADLIB_API	int		MCL_PixelClock(int handle);
MADLIB_API	int		MCL_LineClock(int handle);
MADLIB_API	int		MCL_FrameClock(int handle);
MADLIB_API	int		MCL_AuxClock(int handle);
MADLIB_API	int		MCL_GetClockFrequency(double *adcfreq, double *dacfreq, int handle);

MADLIB_API	double	MCL_GetCalibration(unsigned int axis, int handle);
MADLIB_API	double	MCL_TipTiltHeight(int handle);
MADLIB_API	double	MCL_TipTiltWidth(int handle);
MADLIB_API	int		MCL_MinMaxThetaX(double *min, double *max, int handle);
MADLIB_API	int		MCL_MinMaxThetaY(double *min, double *max, int handle);
MADLIB_API	double	MCL_GetTipTiltThetaX(int handle);
MADLIB_API	double	MCL_GetTipTiltThetaY(int handle);
MADLIB_API	double	MCL_GetTipTiltCenter(int handle);
MADLIB_API	int		MCL_CurrentMinMaxThetaX(double *min, double *max, int handle);
MADLIB_API	int		MCL_CurrentMinMaxThetaY(double *min, double *max, int handle);
MADLIB_API	int		MCL_CurrentMinMaxCenter(double *min, double *max, int handle);
MADLIB_API	int 	MCL_GetFirmwareVersion(short *version, short *profile, int handle);
MADLIB_API	int		MCL_GetSerialNumber(int handle);
MADLIB_API	int		MCL_GetProductInfo(struct ProductInformation *pi, int handle);
MADLIB_API	void	MCL_PrintDeviceInfo(int handle); 
MADLIB_API	bool	MCL_DeviceAttached(int milliseconds, int handle);
MADLIB_API  bool    MCL_CorrectDriverVersion();
MADLIB_API  int     MCL_GetCommandedPosition(double *xCom, double *yCom, double *zCom, int handle);

#ifdef __cplusplus
	}
#endif

#endif