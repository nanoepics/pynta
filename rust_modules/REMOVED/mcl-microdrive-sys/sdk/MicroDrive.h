#ifndef _MICRODRIVE_H_
#define _MICRODRIVE_H_

#define		MCL_SUCCESS				 0
#define     MCL_GENERAL_ERROR		-1
#define		MCL_DEV_ERROR			-2
#define		MCL_DEV_NOT_ATTACHED	-3
#define		MCL_USAGE_ERROR			-4
#define		MCL_DEV_NOT_READY		-5
#define		MCL_ARGUMENT_ERROR		-6
#define		MCL_INVALID_AXIS		-7
#define		MCL_INVALID_HANDLE		-8

#ifdef __cplusplus
	extern"C"{ 
#else
	typedef unsigned char bool;
#endif

#define MICRODRIVE_API __declspec(dllimport)

MICRODRIVE_API	void	MCL_DLLVersion(short *version, short *revision);

MICRODRIVE_API  int		MCL_InitHandle();
MICRODRIVE_API	int		MCL_GrabHandle(short device);
MICRODRIVE_API	int		MCL_InitHandleOrGetExisting();
MICRODRIVE_API	int		MCL_GrabHandleOrGetExisting(short device);
MICRODRIVE_API  int		MCL_GetHandleBySerial(short serial);
MICRODRIVE_API  int		MCL_GrabAllHandles();
MICRODRIVE_API  int		MCL_GetAllHandles(int *handles, int size);
MICRODRIVE_API  int		MCL_NumberOfCurrentHandles();
MICRODRIVE_API  void	MCL_ReleaseHandle(int handle);
MICRODRIVE_API  void	MCL_ReleaseAllHandles();

MICRODRIVE_API	int		MCL_MDStatus(unsigned short* status, int handle);
MICRODRIVE_API	int		MCL_MDStop(unsigned short* status, int handle);
MICRODRIVE_API	int		MCL_MicroDriveMoveStatus(int *isMoving, int handle);
MICRODRIVE_API  int		MCL_MicroDriveWait(int handle);

MICRODRIVE_API int		MCL_MDMoveThreeAxesM(
							int axis1, double velocity1, int microSteps1,
							int axis2, double velocity2, int microSteps2,
							int axis3, double velocity3, int microSteps3,
							int handle);
MICRODRIVE_API int		MCL_MDMoveThreeAxesR(
							int axis1, double velocity1, double distance1, int rounding1,
							int axis2, double velocity2, double distance2, int rounding2, 
							int axis3, double velocity3, double distance3, int rounding3,
							int handle);
MICRODRIVE_API int		MCL_MDMoveThreeAxes(
							int axis1, double velocity1, double distance1,
							int axis2, double velocity2, double distance2,
							int axis3, double velocity3, double distance3,
							int handle);
MICRODRIVE_API int		MCL_MDMoveM(unsigned int axis, double velocity, int microSteps, int handle);
MICRODRIVE_API int		MCL_MDMoveR(unsigned int axis, double velocity, double distance, int rounding, int handle);
MICRODRIVE_API int		MCL_MDMove(unsigned int axis, double velocity, double distance, int handle);
MICRODRIVE_API int		MCL_MDSingleStep(unsigned int axis, int direction, int handle);
MICRODRIVE_API int		MCL_MDResetEncoders(unsigned short* status, int handle);
MICRODRIVE_API int		MCL_MDResetEncoder(unsigned int axis, unsigned short* status, int handle);
MICRODRIVE_API int		MCL_MDReadEncoders(double* e1, double* e2, double *e3, double *e4, int handle);
MICRODRIVE_API int		MCL_MDCurrentPositionM(unsigned int axis, int *microSteps, int handle);
MICRODRIVE_API int		MCL_MDInformation(
							double* encoderResolution,
							double* stepSize,
							double* maxVelocity,
							double* maxVelocityTwoAxis,
							double* maxVelocityThreeAxis,
							double* minVelocity,
							int handle);
MICRODRIVE_API int		MCL_MDEncodersPresent(unsigned char* encoderBitmap, int handle);

MICRODRIVE_API	int 	MCL_GetFirmwareVersion(short *version, short *profile, int handle);
MICRODRIVE_API	int		MCL_GetSerialNumber(int handle);
MICRODRIVE_API	void	MCL_PrintDeviceInfo(int handle); 
MICRODRIVE_API	bool	MCL_DeviceAttached(int milliseconds, int handle);
MICRODRIVE_API  int     MCL_GetProductID(unsigned short *PID, int handle);
MICRODRIVE_API  bool    MCL_CorrectDriverVersion();
MICRODRIVE_API  int     MCL_GetAxisInfo(unsigned char *axis_bitmap, int handle);
MICRODRIVE_API  int     MCL_GetFullStepSize(double *stepSize, int handle);
MICRODRIVE_API	int		MCL_GetTirfModuleCalibration(double *calMM, int handle);

///////////////////////////////////////////////////////////////////////////////
// Legacy functions
///////////////////////////////////////////////////////////////////////////////
MICRODRIVE_API	int		MCL_MicroDriveStatus(unsigned char *status, int handle);
MICRODRIVE_API	int		MCL_MicroDriveStop(unsigned char* status, int handle);
MICRODRIVE_API	int		MCL_MicroDriveMoveProfileXYZ_MicroSteps(
							double velocityX,
							int microStepsX,
							double velocityY,
							int microStepsY,
							double velocityZ,
							int microStepsZ,
							int handle
							);
MICRODRIVE_API	int		MCL_MicroDriveMoveProfile_MicroSteps(
							unsigned int axis,
							double velocity,
							int microSteps,
							int handle
							);
MICRODRIVE_API	int		MCL_MicroDriveMoveProfileXYZ(
							double velocityX,
							double distanceX,
							int roundingX, 
							double velocityY,
							double distanceY,
							int roundingY, 
							double velocityZ,
							double distanceZ,
							int roundingZ,
							int handle
							);
MICRODRIVE_API	int		MCL_MicroDriveMoveProfile(
							unsigned int axis,
							double velocity,
							double distance,
							int rounding,
							int handle
							);
MICRODRIVE_API	int		MCL_MicroDriveSingleStep(unsigned int axis, int direction, int handle);
MICRODRIVE_API	int		MCL_MicroDriveResetEncoders(unsigned char* status, int handle);
MICRODRIVE_API	int		MCL_MicroDriveResetXEncoder(unsigned char* status, int handle);
MICRODRIVE_API	int		MCL_MicroDriveResetYEncoder(unsigned char* status, int handle);
MICRODRIVE_API	int		MCL_MicroDriveResetZEncoder(unsigned char* status, int handle);
MICRODRIVE_API  int		MCL_MicroDriveInformation(
							double* encoderResolution,
							double* stepSize,
							double* maxVelocity,
							double* maxVelocityTwoAxis,
							double* maxVelocityThreeAxis,
							double* minVelocity,
							int handle);
MICRODRIVE_API	int		MCL_MicroDriveReadEncoders(double* x, double* y, double *z, int handle);
MICRODRIVE_API	int		MCL_MicroDriveCurrentMicroStepPosition(int *microStepsX, int *microStepsY, int *microStepsZ, int handle);
MICRODRIVE_API int		MCL_MD1MoveProfile_MicroSteps(double velocity, int microSteps, int handle);
MICRODRIVE_API int		MCL_MD1MoveProfile(double velocity, double distance, int rounding, int handle);
MICRODRIVE_API int		MCL_MD1SingleStep(int direction, int handle);
MICRODRIVE_API int		MCL_MD1ResetEncoder(unsigned char* status, int handle);
MICRODRIVE_API int		MCL_MD1ReadEncoder(double* position, int handle);
MICRODRIVE_API int		MCL_MD1CurrentMicroStepPosition(int *microSteps, int handle);
MICRODRIVE_API int		MCL_MD1Information(
							double* encoderResolution,
							double* stepSize,
							double* maxVelocity,
							double* minVelocity,
							int handle);


#ifdef __cplusplus
	}
#endif

#endif